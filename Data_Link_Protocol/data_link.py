import time
import board
from digitalio import DigitalInOut
from circuitpython_nrf24l01.rf24 import RF24

# Initialize nRF24L01 radio
# Assuming CE_PIN and CSN_PIN are set up externally and SPI_BUS is initialized
CE_PIN = DigitalInOut(board.D22)  # Example pin, replace with your actual CE pin
CSN_PIN = DigitalInOut(board.D17)  # Example pin, replace with your actual CSN pin
nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)

# nRF24L01 basic setup
nrf.pa_level = -18  # Power Amplifier level
nrf.data_rate = RF24.DATA_RATE_1MBPS  # Data rate
communication_address = b"1Node"  # Single address for both TX and RX

def transmit(buffer):
    """Function to transmit a buffer"""
    nrf.open_tx_pipe(communication_address)  # Set the transmit address
    nrf.listen = False  # Ensure it's in transmit mode

    # Attempt to send the buffer
    if nrf.send(buffer):
        print("Data sent successfully")
    else:
        print("Sending failed")

def receive(timeout=10):
    """Function to receive data"""
    nrf.open_rx_pipe(1, communication_address)  # Set the receive address
    nrf.listen = True  # Listen for incoming transmissions

    start = time.monotonic()  # Start timer
    received_payload = bytearray()

    while (time.monotonic() - start) < timeout:
        if nrf.available():
            while nrf.available():
                received_payload += nrf.read(nrf.any())  # Read payload
            print("Received data:", received_payload)
            break

    nrf.listen = False  # Stop listening
    return received_payload

# Example usage
if __name__ == "__main__":
    role = input("Choose role: (T)ransmitter or (R)eceiver? ").lower()

    if role == "t":
        # Assuming data_buffer is the data you want to transmit
        data_buffer = b"Hello, nRF24L01+"  # Replace with your data buffer
        transmit(data_buffer)
    elif role == "r":
        print("Receiving data...")
        received_data = receive()
        print("Received:", received_data)
    else:
        print("Invalid role selected.")

