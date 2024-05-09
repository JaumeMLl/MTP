import time
import RPi.GPIO as GPIO
import os
import shutil
import numpy as np
import subprocess

from Constants_Network_Mode import *

def set_pipes(comms_info, nrf):
    nrf.open_rx_pipe(1, comms_info.listening_pipe_address)
    nrf.open_tx_pipe(comms_info.destination_pipe_address)

def wait_for_desired_message(comms_info, desired_message, timeout, nrf):
    """
    Waits until it receives the message matching the desired value on the given pipe, or until the timeout_ms expires.
    
    Parameters:
    - listening_pipe_address: The pipe being listened to for incoming messages.
    - destination_pipe_address: The pipe where the response should be sent.
    - desired_message: The specific message expected to be received.
    - timeout: Timeout period in seconds.

    Returns:
    - True if the desired_message is received within the timeout period, False otherwise.
    """
    nrf.listen = True  # put radio into RX mode and power up

    start = time.monotonic()

    while (time.monotonic() - start) < timeout:
        if nrf.available():
            # Read the received message
            received_message = []
            received_message = nrf.read()
            print(f"Received Message: {received_message}")

            actual_message = received_message[5+2:]  # Skip 5 bytes for responder ID and 2 bytes for separator ": "

            # Check if the responder ID matches and the actual message is the desired one
            if actual_message == desired_message:
                print(f"Desired Message {desired_message} received")
                # Extract the responder ID and the actual message from the received message
                comms_info.destination_pipe_address = bytes(received_message[:5])
                return True  # Message received successfully
            else:
                print("Message not recognized")
        time.sleep(0.1)  # Wait for a short time before checking again
    
    print(f"Desired Message {desired_message} NOT received")
    return False

def wait_long_desired_message(comms_info, desired_message, timeout, nrf):
    """
    Waits until it receives the message matching the desired value on the given pipe, or until the timeout_ms expires.
    
    Parameters:
    - listening_pipe_address: The pipe being listened to for incoming messages.
    - destination_pipe_address: The pipe where the response should be sent.
    - desired_message: The specific message expected to be received.
    - timeout: Timeout period in seconds.

    Returns:
    - True if the desired_message is received within the timeout period, False otherwise.
    """
    nrf.listen = True  # put radio into RX mode and power up

    start = time.monotonic()
    

    while not nrf.available():
        a=1
    if nrf.available():
        # Read the received message
        received_message = []
        received_message = nrf.read()
        print(f"Received Message: {received_message}")

        actual_message = received_message[5+2:]  # Skip 5 bytes for responder ID and 2 bytes for separator ": "

        # Check if the responder ID matches and the actual message is the desired one
        if actual_message == desired_message:
            print(f"Desired Message {desired_message} received")
            # Extract the responder ID and the actual message from the received message
            comms_info.destination_pipe_address = bytes(received_message[:5])
            return True  # Message received successfully
        else:
            print("Message not recognized")
    time.sleep(0.1)  # Wait for a short time before checking again
    
    print(f"Desired Message {desired_message} NOT received")
    return False

def send_message(destination_pipe_address, message, nrf):
    nrf.listen = False  # Dejar de escuchar para poder enviar
    nrf.open_tx_pipe(destination_pipe_address)
    data_to_send = MY_PIPE_ID+b": "+ message
    print(f"About to send: {data_to_send}", "TO:", destination_pipe_address)
    sent_successfully = nrf.send(data_to_send)  # Enviar el mensaje de confirmación
    print("aadf")
   
    if sent_successfully:
        print(f"{message} sent successfully.")
        return True
    else:
        print(f"Failed to send {message}.")
        return False

def transmitter(comms_info, filelist, count, nrf):
    #TODO implement transmitter
    time.sleep(1)
    r = False
    path = FOLDER_PATH  # Ruta completa al archivo en el directorio /mnt/usbdrive
    filelist = np.array([os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]) # Get the list of files in the directory
    filelist = filelist[np.where([x.endswith(".txt") and not x.startswith(".") for x in filelist])[0]] # Get the elements that end with ".txt" and does not start with "."
    filepath = filelist[0]
    with open(filepath, 'rb') as file:
        file_content = file.read()
    #nrf.auto_ack = True
    nrf.ack=False
    nrf.listen = False  
    chunk_size = 31 
    stop_wait = False
    total_chunks = len(file_content) // (chunk_size) + (1 if len(file_content) % (chunk_size) else 0)
    for i in range(total_chunks):
        start = i * (chunk_size)
        end = start + (chunk_size)
        chunk = file_content[start:end]
        if len(chunk) < chunk_size:
            chunk += b'\x00' * (chunk_size - len(chunk))
        result = send_chunk_sw(chunk, nrf)
        print(result)
        print((i+1)/total_chunks, " %")
        r = True

    if r:
        print("Package Transmission Accomplished")
    else:
        print("Package Transmission Failed")
    return r 

tx_bit_flip = 0

def send_chunk_sw(buffer, nrf):
    global tx_bit_flip
    first_byte = tx_bit_flip
    buffer = bytes([first_byte]) + buffer
    result = nrf.send(buffer)
    while not result:
        print("ERROR")
        result = nrf.send(buffer)
    tx_bit_flip ^= 1
    return result

rx_bit_flip = 0

def receiver(comms_info, timeout, nrf):
    global rx_bit_flip
    print("starting reception")
    nrf.channel = CHANNEL2
    #nrf.auto_ack=True
    nrf.ack = False
    #nrf.auto_ack=False
    nrf.ack=False
    timeout = 3
    nrf.listen = True
    stop_wait = False
    received_data = bytearray()
    start = time.monotonic()
    while (time.monotonic() - start) < timeout:
        if nrf.available():
            while nrf.available():
                buffer = nrf.read(nrf.any())
                received_bit_flip = buffer[0]
                print("BIT RECEIVED:", received_bit_flip, "EXPECTED BIT: ", rx_bit_flip)
                if received_bit_flip == rx_bit_flip or not stop_wait:
                    print("Received chunk: {}...".format(buffer[:10]))
                    received_data += buffer[1:]  
                    rx_bit_flip ^= 1
                else :
                    print("Out of sequence packet")
            start = time.monotonic()
    nrf.listen = False
    valid_data_end = len(received_data.rstrip(b'\x00'))
    valid_data = received_data[:valid_data_end]
    if len(valid_data) == 0 :
        print("Empty")
        return False
    
    with open(FILE_NAME, "wb") as file:
        file.write(valid_data)
        print(f"Archivo reconstruido y guardado. Tamaño total: {len(received_data)} bytes.")
    #nrf.auto_ack=False

    txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]

    # Copy the extracted .txt file to the USB directory
    try:
        for txt_file in txt_files:
            shutil.copy(txt_file, FOLDER_PATH)
            print(f"Received message '{txt_file}' also stored in '/media/usb/'")
            #newfile_leds()
            #blink_success_leds(10, USB_LED, USB_LED) 
            #reset_leds()
    except Exception as e:
        print(f"Failed to save the message in '/media/usb'. Error: {e}")

    return True

# Initialize the leds
GPIO.setmode(GPIO.BCM)

GPIO.setup(FILE_POSSESION_LED, GPIO.OUT)
GPIO.setup(FILE_REQUEST_LED, GPIO.OUT)
GPIO.setup(REQUEST_ACC_LED, GPIO.OUT)
GPIO.setup(TRANSMIT_ACC_LED, GPIO.OUT)
GPIO.setup(USB_LED, GPIO.OUT)
GPIO.setup(NM_SWITCH, GPIO.IN)
GPIO.setup(TXRX_SWITCH, GPIO.IN)

def wait_for_usb():
   # Check number of files in the USB drive
    num_devices = 0
    while num_devices < 2:
        df = subprocess.check_output("lsusb")
        df = df.split(b'\n')
        num_devices = len(df)-1
        time.sleep(1)
    GPIO.output(USB_LED, GPIO.HIGH)

def reset_leds():
    """Turn off all LEDs."""
    GPIO.output(FILE_REQUEST_LED, GPIO.LOW)
    GPIO.output(REQUEST_ACC_LED, GPIO.LOW)
    GPIO.output(TRANSMIT_ACC_LED, GPIO.LOW)
    GPIO.output(FILE_POSSESION_LED, GPIO.LOW)
    GPIO.output(USB_LED, GPIO.LOW)