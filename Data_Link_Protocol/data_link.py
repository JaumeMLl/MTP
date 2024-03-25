import time
import board
import os as sys
from digitalio import DigitalInOut
from circuitpython_nrf24l01.rf24 import RF24

def readFile():
    
    # Get Path 
    # TO DO: Change path to USB path
    path = '/home/pi/usb/documento.txt'

    # Open file
    try:
        with open(path, 'r') as file:
            content = file.read()
            print("File contet:")
            print(content)
    except FileNotFoundError:
        print(f"The file {path} does not exist.")
    except Exception as e:
        print(f"There was a mistake while opening the file: {e}")
    
    # Fragment file
    payload_size = 32

    # TO DO: Falta completar el readFile(), fragmentar i retornar un string list, després a l'hora 
    # d'enviar s'ha de fer un count i un bucle per enviar en aquest ordre.
    # return list(string[0+i: length+i] for i in range(0, len(string), length))


# Initialize nRF24L01 radio
SPI_BUS, CSN_PIN, CE_PIN = (None, None, None)

#SPI 
# Found this on: https://circuitpython-nrf24l01.readthedocs.io/en/latest/examples.html#simple-test
try:  #on Linux
    import spidev

    SPI_BUS = spidev.SpiDev()
    CSN_PIN = DigitalInOut(board.D17)  # Example pin, replace with your actual CSN pin
    CE_PIN = DigitalInOut(board.D22)  # Example pin, replace with your actual CE pin

except ImportError: #CircuitPython
    # using board.SPI() automatically selects the MCU's
    # available SPI pins, board.SCK, board.MOSI, board.MISO
    SPI_BUS = board.SPI()   #init spi bus object

    # change these (digital output) pins accordingly
    CE_PIN = DigitalInOut(board.D4)
    CSN_PIN = DigitalInOut(board.D5)

# initialize the nRF24L01 on the spi bus object
nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)
# On Linux, csn value is a bit coded
#                 0 = bus 0, CE0  # SPI bus 0 is enabled by default
#                10 = bus 1, CE0  # enable SPI bus 2 prior to running this
#                21 = bus 2, CE1  # enable SPI bus 1 prior to running this

# nRF24L01 basic setup
nrf.pa_level = -18  # Power Amplifier level
nrf.data_rate = RF24.DATA_RATE_1MBPS  # Data rate
#communication_address = b"1Node"  # Single address for both TX and RX
# addresses needs to be in a buffer protocol object (bytearray)
communication_address = [b"1Node", b"2Node"] # Adress 0 for transmitter and 1 for receiver. Default is for transmitter

# to use different addresses on a pair of radios, we need a variable to
# uniquely identify which address this radio will use to transmit
# 0 uses address[0] to transmit, 1 uses address[1] to transmit
radio_number = bool(
    int(input("Which radio is this? Enter '0' or '1'. Defaults to '0' ") or 0)
)

# set TX address of RX node into the TX pipe
nrf.open_tx_pipe(communication_address[radio_number])  # always uses pipe 0

# set RX address of TX node into an RX pipe
nrf.open_rx_pipe(1, communication_address[not radio_number])  # using pipe 1


def transmit(buffer):
    """Function to transmit a buffer"""
    nrf.listen = False  # Ensure it's in transmit mode
    # Read and fragment the file
    buffer = readFile()

    # Attempt to send the buffer --> aixi no perque s'ha de partir
    if nrf.send(buffer):
        print("Data sent successfully")
    else:
        print("Sending failed")


def receive(timeout=10):
    """Function to receive data"""
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