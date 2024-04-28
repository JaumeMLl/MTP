import time
from Constants_Network_Mode import *

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
    nrf.open_rx_pipe(1, comms_info.listening_pipe_address)
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
                comms_info.destination_pipe_address = received_message[:5]
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

def transmitter(comms_info, filelist, count):
    #TODO set channel
    
    # set TX address of RX node into the TX pipe
    nrf.open_tx_pipe(comms_info.destination_pipe_address)

    # set RX address of TX node into an RX pipe
    nrf.open_rx_pipe(1, comms_info.listening_pipe_address)

    nrf.listen = False  # ensure the nRF24L01 is in TX mode

    #with open(filepath, 'r') as file:
    #    message = file.read().encode()
    
    ## TODO: fix this. It is not working
    # message = b''
    # for filepath in filelist:
    #     file = open(filepath,'rb')
    #     message += file.read()
    
    filepath = filelist[-1]
    # This line stores the filename in the message
    message = open(filepath, 'rb').read() + b'separaciofitxer' + bytes(filepath.split('/')[-1], 'utf-8')

    chunks = [message[i:i + 32] for i in range(0, len(message), 32)]

    for chunk in chunks:
        attempt = 0
        while attempt < count:
            print(f"Sending chunk: {chunk}")
            nrf.send(chunk)  # Enviar el chunk
            nrf.listen = True  # Cambiar al modo RX para esperar el ACK

            start_time = time.monotonic()  # Iniciar el temporizador
            while time.monotonic() - start_time < 5:  # Esperar hasta 5 segundos para recibir el ACK
                if nrf.available():  # Verificar si hay un mensaje disponible
                    received_payload = nrf.read()  # Leer el payload recibido
                    if received_payload == b'ACK':  # Si se recibe el ACK esperado
                        print("ACK received. Sending next chunk.")
                        attempt = count  # Salir del bucle de reintento
                        break  # Salir del bucle de espera
                time.sleep(0.1)  # Pequeña pausa para evitar sobrecargar la CPU

            nrf.listen = False  # Cambiar de nuevo al modo TX después de esperar el ACK

            if attempt < count - 1:  # Si no se recibió el ACK, reintento
                print("No ACK received. Retrying...")
            attempt += 1

        if attempt == count:  # Si se agotaron los intentos sin recibir ACK
            print("Failed to receive ACK after maximum attempts. Moving to the next chunk.")
            # Opcional: podrías elegir terminar el envío completamente aquí si es crítico
            # break

    print("Message transmission complete.")

def receiver(comms_info, timeout):
    # set TX address of RX node into the TX pipe
    nrf.open_tx_pipe(comms_info.destination_pipe_address)

    # set RX address of TX node into an RX pipe
    nrf.open_rx_pipe(1, comms_info.listening_pipe_address)

    nrf.listen = True  # put radio into RX mode and power up

    message = []  # list to accumulate message chunks
    start = time.monotonic()

    while (time.monotonic() - start) < timeout:
        if nrf.available():
            received_payload = nrf.read()  # Leer el mensaje entrante
            print(f'Received payload: {received_payload}')
            message.append(received_payload)

            # Preparar y enviar un mensaje de confirmación de vuelta al transmisor
            ack_payload = b'ACK'  # Mensaje de confirmación
            nrf.listen = False  # Dejar de escuchar para poder enviar
            sent_successfully = nrf.send(ack_payload)  # Enviar el mensaje de confirmación

            if sent_successfully:
                print("Confirmation message sent successfully.")
            else:
                print("Failed to send confirmation message.")

            nrf.listen = True  # Volver al modo de escucha después de enviar
            start = time.monotonic()  # Restablecer el temporizador

    # Concatenar y procesar el mensaje completo recibido, si es necesario
    complete_message = b''.join(message)
    print(f"Complete message received: {complete_message}")

    # Opcional: Guardar el mensaje completo en un archivo
    filename = complete_message.split(b'separaciofitxer')[-1].decode('utf-8')
    long_desc = len(filename) + len(b'separaciofitxer')
    complete_message = complete_message[:-long_desc]
    with open(filename, 'wb') as file:
        file.write(complete_message)

    print("Received message stored in",filename)

    # Guardar también el mensaje completo en un archivo en /mnt/usbdrive
    try:
        with open('/media/usb/'+filename, 'wb') as file:
            file.write(complete_message)
        print("Received message also stored in '/media/usb/'",filename)
    except Exception as e:
        print(f"Failed to save the message in '/media/usb'. Error: {e}")
    nrf.listen = False  # Se recomienda mantener el transceptor en modo TX mientras está inactivo