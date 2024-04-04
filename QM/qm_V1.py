"""
Simple example of using the RF24 class.
"""
import time
import struct
import board
from digitalio import DigitalInOut

# if running this on a ATSAMD21 M0 based board
# from circuitpython_nrf24l01.rf24_lite import RF24
from circuitpython_nrf24l01.rf24 import RF24

# invalid default values for scoping
SPI_BUS, CSN_PIN, CE_PIN = (None, None, None)

try:  # on Linux
    import spidev

    SPI_BUS = spidev.SpiDev()  # for a faster interface on linux
    CSN_PIN = 0  # use CE0 on default bus (even faster than using any pin)
    CE_PIN = DigitalInOut(board.D25)  # using pin gpio22 (BCM numbering)

except ImportError:  # on CircuitPython only
    # using board.SPI() automatically selects the MCU's
    # available SPI pins, board.SCK, board.MOSI, board.MISO
    SPI_BUS = board.SPI()  # init spi bus object

    # change these (digital output) pins accordingly
    CE_PIN = DigitalInOut(board.D4)
    CSN_PIN = DigitalInOut(board.D5)


# initialize the nRF24L01 on the spi bus object
nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)
# On Linux, csn value is a bit coded
#                 0 = bus 0, CE0  # SPI bus 0 is enabled by default
#                10 = bus 1, CE0  # enable SPI bus 2 prior to running this
#                21 = bus 2, CE1  # enable SPI bus 1 prior to running this

# canviar si es necessari
nrf.pa_level = -12

# addresses needs to be in a buffer protocol object (bytearray)
address = [b"1Node", b"2Node"]

radio_number = bool(
    int(input("Which radio is this? Enter '0' or '1'. Defaults to '0' ") or 0)
)

# set TX address of RX node into the TX pipe
nrf.open_tx_pipe(address[radio_number])  # always uses pipe 0

# set RX address of TX node into an RX pipe
nrf.open_rx_pipe(1, address[not radio_number])  # using pipe 1

def calculate_checksum(data):
    """Calculates a simple checksum of the given data."""
    return sum(data) & 0xFF

def master(filepath, count=1, timeout=500):
    nrf.listen = False  # ensure the nRF24L01 is in TX mode

    # Read the content of the file
    with open(filepath, 'r') as file:
        message = file.read().encode()  # read the content and convert to bytes

    # Divide el mensaje en chunks de 30 bytes para dejar espacio para el número de secuencia y checksum
    chunks = [message[i:i + 30] for i in range(0, len(message), 30)]

    for chunk_number, chunk in enumerate(chunks):
        sequence_byte = struct.pack('B', chunk_number % 256)  # Un byte para el número de secuencia
        checksum = calculate_checksum(chunk)
        chunk_with_metadata = sequence_byte + chunk + struct.pack('B', checksum)

        # Asegúrate de que el tamaño total es <= 32 bytes
        if len(chunk_with_metadata) > 32:
            raise ValueError(f"El fragmento excede el tamaño máximo permitido. Tamaño: {len(chunk_with_metadata)} bytes.")

        attempt = 0
        ack_received = False
        while attempt < count and not ack_received:
            print(f"Sending chunk {chunk_number + 1}/{len(chunks)}: {chunk_with_metadata}")
            nrf.send(chunk_with_metadata)
            nrf.listen = True  # start listening for ACK
            start = time.monotonic()
            while time.monotonic() - start < timeout:
                if nrf.available():
                    received_payload = nrf.read()
                    if received_payload == b'ACK':
                        ack_received = True
                        print(f"ACK Received for chunk {chunk_number + 1}")
                        break
            nrf.listen = False  # stop listening, prepare to send next chunk
            if not ack_received:
                print(f"No ACK received for chunk {chunk_number + 1}, resending...")
                attempt += 1

        if not ack_received:
            print("Failed to receive ACK after several attempts, aborting send.")
            break  # Exit the for loop if we failed to send a chunk

        time.sleep(0.1)  # short delay before sending the next chunk

    if ack_received:
        print("All chunks sent successfully.")


def slave(timeout=6):
    nrf.listen = True  # put radio into RX mode and power up
    expected_sequence = 0
    message = []  # list to accumulate message chunks

    while True:
        if nrf.available():
            buffer = nrf.read()  # fetch the payload
            sequence, *data, received_checksum = struct.unpack('B' * len(buffer), buffer)
            data = bytes(data)
            if sequence == expected_sequence and calculate_checksum(data) == received_checksum:
                message.append(data)
                expected_sequence = (expected_sequence + 1) % 256  # increment sequence
                nrf.send(b'ACK')  # send ACK only if the chunk is valid
                print(f"Received and acknowledged chunk {sequence}.")
            else:
                print(f"Invalid chunk or out of order: {sequence}.")
        elif time.monotonic() - start > timeout:
            break

    # Concatenate all chunks and decode to a string
    complete_message = b"".join(message).decode()
    print(f"Received message: {complete_message}")
    nrf.listen = False  # recommended behavior is to keep in TX mode while idle



def set_role():
    """Set the role using stdin stream."""
    role_input = input(
        "*** Enter 'R' for receiver role.\n"
        "*** Enter 'T' followed by a space and your message for transmitter role.\n"
        "*** Enter 'Q' to quit example.\n"
    ).strip()

    if role == 'R':
        slave()
        return True
    elif role == 'T':
        filepath = 'mtp.txt'  # Define the name of the file here
        master(filepath)
        return True
    elif role == 'Q':
        nrf.power = False
        return False
    else:
        print(role, "is an unrecognized input. Please try again.")
        return set_role()


if __name__ == "__main__":
    try:
        while set_role():
            pass  # continue example until 'Q' is entered
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
else:
    print("    Run slave() on receiver\n    Run master() on transmitter")
