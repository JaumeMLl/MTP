import time
import RPi.GPIO as GPIO
import os

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
    r = False
    file_path = FOLDERPATH+FILE_NAME
    with open(file_path, 'rb') as file:
        file_content = file.read()
    #nrf.auto_ack = False
    nrf.listen = False  
    chunk_size = 31 
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

global tx_bit_flip
tx_bit_flip = 0

def send_chunk_sw(buffer, nrf):
    first_byte = tx_bit_flip
    buffer = bytes([first_byte]) + buffer
    #nrf.auto_ack = False
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
    nrf.listen = True
    stop_wait = False
    #nrf.load_ack(b"0",1)
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
    with open(FOLDERPATH+FILE_NAME, "wb") as file:
        file.write(valid_data)
        print(f"Archivo reconstruido y guardado. Tamaño total: {len(received_data)} bytes.")
    #nrf.auto_ack=False
    return True

