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
    print(f"About to send: {data_to_send}")
    sent_successfully = nrf.send(data_to_send)  # Enviar el mensaje de confirmación
   
    if sent_successfully:
        print(f"{message} sent successfully.")
        return True
    else:
        print(f"Failed to send {message}.")
        return False

def transmitter(comms_info, filelist, count, nrf):
    #TODO implement transmitter
    time.sleep(5)
    print("TODO implement")  

def receiver(comms_info, timeout, nrf):
    #TODO implement receiver
    time.sleep(5)
    print("TODO implement")