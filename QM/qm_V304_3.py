import time
import struct
import board
import chardet
import sys
import subprocess
from digitalio import DigitalInOut

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

# Change the Power Amplifier level
nrf.pa_level = -12

# addresses needs to be in a buffer protocol object (bytearray)
address = [b"1Node", b"2Node"]

# to use different addresses on a pair of radios, we need a variable to
# uniquely identify which address this radio will use to transmit
# 0 uses address[0] to transmit, 1 uses address[1] to transmit
radio_number = bool(
    int(input("Which radio is this? Enter '0' or '1'. Defaults to '0' ") or 0)
)

# set TX address of RX node into the TX pipe
nrf.open_tx_pipe(address[radio_number])  # always uses pipe 0

# set RX address of TX node into an RX pipe
nrf.open_rx_pipe(1, address[not radio_number])  # using pipe 1

def read_file(filepath):
    try: 
        # Use chardet to detect the encoding, open with 'rb' so it reads as binary
        with open(filepath, 'rb') as rawfile:
            rawdata = rawfile.read()
            result = chardet.detect(rawdata)
            encoding = result['encoding']
        
        #Now, read the file with the detected encoding
        with open(filepath, 'r', encoding=encoding) as file: 
            message = file.read()
            print(f"Successfully read with encoding: {encoding}")
            return message

    except UnicodeDecodeError:
        print(f"Failed with encoding: {encoding}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return 'File incorrectly red or empty file in this path' 

# Need to mount the USB on the rpistr location 
def get_file_path():
    rpistr = "/media/mtp/" # Location where the USB is located
    proc = subprocess.Popen("ls " + rpistr, shell=True, preexec_fn=sys.setsid, stdout=subprocess.PIPE)
    line = proc.stdout.readline().decode("utf-8").strip()  # Decoding bytes to string and stripping newline character
    print(line)
    filepath = rpistr + line + "/"  # Concatenating strings to form path
    print('USB Path:', filepath)
    return filepath

def write_file(complete_message):
    path = "/media/mtp/MTP/"
   
    destination_path = path + "resultado.txt"
    with open(destination_path, 'w') as file:
        file.write(complete_message)

    print("Received message stored in '{}'".format(destination_path))  
    

def master(count=1):
    nrf.listen = False  # ensure the nRF24L01 is in TX mode
    filepath = get_file_path()
    message = read_file(filepath)

    # Divide the message into 32-byte chunks
    chunks = [message[i:i + 32] for i in range(0, len(message), 32)]

    while count:
        for chunk in chunks:
            start_timer = time.monotonic_ns()  # start timer
            result = nrf.send(chunk)
            end_timer = time.monotonic_ns()  # end timer
            if not result:
                print("send() failed or timed out")
            else:
                print(
                    "Chunk sent successfully! Time to Transmit:",
                    "{} us. Chunk: {}".format((end_timer - start_timer) / 1000, chunk)
                )
            # Wait for ACK from the receiver
                ack_received = False
                timeout = 2  # Timeout in seconds
                start_time = time.monotonic()
                while (time.monotonic() - start_time) < timeout:
                    if nrf.available():
                        ack = nrf.read()
                        if ack == b'ACK':
                            ack_received = True
                            break
                if ack_received:
                    print("ACK received successfully.")
                    break  # Move to the next chunk
                else:
                    print("Timeout: No ACK received. Resending...")
        count -= 1
        print("One message cycle complete, remaining:", count)

def slave(timeout=6):
    nrf.listen = True  # put radio into RX mode and power up

    message = []  # list to accumulate message chunks
    start = time.monotonic()

    while (time.monotonic() - start) < timeout:
        while nrf.available():
            # fetch payloads from RX FIFO until it's empty
            buffer = nrf.read()
            print(f'Buffer: {buffer}')  # Puedes quitar este print si ya no lo necesitas
            message.append(buffer)
            # reset the start time upon successful reception
            start = time.monotonic()

    # Concatenate all chunks and decode to a string
    complete_message = b"".join(message).decode()

    # Writing the received message to a file
    write_file(complete_message)

    nrf.listen = False  # recommended behavior is to keep in TX mode while idle


def set_role():
    """Set the role using stdin stream."""
    role = input(
        "*** Enter 'R' for receiver role.\n"
        "*** Enter 'T' for transmitter role\n"
        "*** Enter 'Q' to quit example.\n"
    ).strip().upper()

    if role == 'R':
        slave()
        return True
    elif role == 'T':
        master()
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
