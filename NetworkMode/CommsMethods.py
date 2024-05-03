import time
import RPi.GPIO as GPIO
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
    print(f"About to send: {data_to_send}")
    sent_successfully = nrf.send(data_to_send)  # Enviar el mensaje de confirmación
   
    if sent_successfully:
        print(f"{message} sent successfully.")
        return True
    else:
        print(f"Failed to send {message}.")
        return False

def transmitter(comms_info, filelist, count, nrf):
    #TODO set channel
    # TODO escapar del ack True. No entrar en bucle

    # set TX address of RX node into the TX pipe
    nrf.open_tx_pipe(comms_info.destination_pipe_address)

    # set RX address of TX node into an RX pipe
    nrf.open_rx_pipe(1, comms_info.listening_pipe_address)

    nrf.autoack = True
    nrf.listen = False  # ensure the nRF24L01 is in TX mode
    GPIO.output(TRANSMITTER_LED, GPIO.HIGH)
    '''
    nrf.flush_tx()
    nrf.flush_rx()  # Vaciar el búfer de recepción
    fifo_state_tx = nrf.fifo(True)
    fifo_state_rx = nrf.fifo(False)
    while fifo_state_tx != 2 and fifo_state_rx != 2:
        nrf.flush_tx()
        nrf.flush_rx()  # Vaciar el búfer de recepción
        print('fifo state TX:',fifo_state_tx)
        print('fifo state RX:',fifo_state_rx)
        fifo_state_rx = nrf.fifo(False)
        fifo_state_tx = nrf.fifo(True)
    '''
    for i in range(10):
        nrf.send(b'hola')
        nrf.read()
    fifo_state_tx = nrf.fifo(True)
    print('fifo state TX:',fifo_state_tx)
    filepath = filelist[0]
    print(f"Sending file: {filepath}")
    
    # Compress the file using 7z
    os.system(f"yes | 7z a {filepath}.7z {filepath}")
    filepath = filepath + ".7z"
    
    # This line stores the filename in the message
    message = open(filepath, 'rb').read() + b'separaciofitxer' + bytes(filepath.split('/')[-1], 'utf-8')

    chunks = [message[i:i + 32] for i in range(0, len(message), 32)]
    
    result = nrf.send(b'Ready')
    print('fifo state TX1:',fifo_state_tx)
    while not result:
        time.sleep(0.1)
        result = nrf.send(b'Ready')

    print("Receiver is ready to receive.")
    
    for chunk in chunks:
        result = nrf.send(chunk)  # Enviar el chunk
        # received_payload = nrf.read()  # Leer el payload recibido
        if result:  # Si se recibe el ACK esperado
            print("ACK received. Sending next chunk.")
            GPIO.output(CONNECTION_LED, GPIO.HIGH)
        else:
            while not result:
                print("No ACK received. Retrying...")
                result = nrf.send(chunk)
                GPIO.output(CONNECTION_LED, GPIO.LOW)
                #time.sleep(0.5)

        # Show percentage of message sent
        print(f"Percentage of message sent: {round((chunks.index(chunk)+1)/len(chunks)*100, 2)}%")
    
    print("Message transmission complete.")
    ack_payload = b'FINALTRANSMISSIO'  # Mensaje de finalización
    nrf.listen = False  # Dejar de escuchar para poder enviar
    sent_successfully = nrf.send(ack_payload)  # Enviar el mensaje de confirmación
    if sent_successfully:
        print("Confirmation message sent successfully.")
        blink_success_leds(10, CONNECTION_LED, NM_LED)
        reset_leds()
    else:
        print("Failed to send confirmation message.")
        sent_successfully = nrf.send(ack_payload)
        while not sent_successfully:
            sent_successfully = nrf.send(ack_payload)
            time.sleep(0.5)
        print("Confirmation message sent successfully.")
        GPIO.output(CONNECTION_LED, GPIO.LOW)

    nrf.autoack = False

    print("Message transmission complete.")

def receiver(comms_info, timeout, nrf):
    nrf.autoack = True
    nrf.listen = True  # put radio into RX mode and power up
    nrf.flush_tx()
    nrf.flush_rx()  # Vaciar el búfer de recepción
    nrf.flush_tx()
    nrf.flush_rx()  # Vaciar el búfer de recepción
    nrf.flush_tx()
    nrf.flush_rx()  # Vaciar el búfer de recepción
    GPIO.output(RECEIVER_LED, GPIO.HIGH)
    message = []  # list to accumulate message chunks
    start = time.monotonic()
    print("Waiting for start message...")
    received_payload = nrf.read()  # Leer el mensaje entrante
    while received_payload != b'Ready':
        received_payload = nrf.read()
        
    print("Waiting for incoming message...")
    while (time.monotonic() - start) < timeout:
        GPIO.output(CONNECTION_LED, GPIO.LOW)
        if nrf.available():
            received_payload = nrf.read()  # Leer el mensaje entrante
            if received_payload == b'FINALTRANSMISSIO':
                # Mensaje transmission complete
                print("Message transmission complete.")
                break
            else:
                # print(f'Received payload: {received_payload}')
                message.append(received_payload)
                GPIO.output(CONNECTION_LED, GPIO.HIGH)

            start = time.monotonic()  # Restablecer el temporizador
            
    # Concatenar y procesar el mensaje completo recibido, si es necesario
    complete_message = b''.join(message)
    print(f"Complete message received: {complete_message}")
    nrf.autoack = False

    filename = complete_message.split(b'separaciofitxer')[-1].decode('utf-8')
    long_desc = len(filename) + len(b'separaciofitxer')
    complete_message = complete_message[:-long_desc]
    with open(filename, 'wb') as file:
        file.write(complete_message)
    
    # # # Extract the zip file
    # # os.system(f"unzip -j {filename} -d .")
    
    # Extract the 7z file
    output = os.system(f"yes | 7z x {filename} -o.")

    if output == 0:
        print("File decompressed successfully")
        blink_success_leds(10, CONNECTION_LED, NM_LED)
    else:
        print("Error decompressing the file")
        blink_failure_leds(5)

    # Buscar los archivos .txt en el directorio de trabajo
    txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]

    print("Received message stored in",txt_files)

    # Copy the extracted .txt file to the USB directory
    try:
        for txt_file in txt_files:
            shutil.copy(txt_file, '/media/usb/')
            print(f"Received message '{txt_file}' also stored in '/media/usb/'")
            #blink_success_leds(10, USB_LED, USB_LED) 
            #reset_leds()
    except Exception as e:
        print(f"Failed to save the message in '/media/usb'. Error: {e}")