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
            # Extract the responder ID and the actual message from the received message
            comms_info.destination_pipe_address = received_message[:5]
            actual_message = received_message[5+2:]  # Skip 5 bytes for responder ID and 2 bytes for separator ": "

            # Check if the responder ID matches and the actual message is the desired one
            if actual_message == desired_message:
                print("Message received")
                return True  # Message received successfully
            else:
                print("Message not recognized")
        time.sleep(0.1)  # Wait for a short time before checking again
    
    print("Message not received")
    return False

def send_message(comms_info, message, nrf):
    print(f"Channel Information: {comms_info}")

    nrf.listen = False  # Dejar de escuchar para poder enviar
    nrf.open_tx_pipe(comms_info.destination_pipe_address)
    data_to_send = MY_PIPE_ID+b": "+ message
    print(f"About to send: {data_to_send}")
    sent_successfully = nrf.send(data_to_send)  # Enviar el mensaje de confirmación
   
    if sent_successfully:
        print(f"{message} sent successfully.")
    else:
        print(f"Failed to send {message}.")

    nrf.listen = True  # Volver al modo de escucha después de enviar