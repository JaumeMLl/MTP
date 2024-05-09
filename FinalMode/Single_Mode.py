import time
import board
from digitalio import DigitalInOut
import os
import subprocess
import RPi.GPIO as GPIO
import numpy as np
import shutil
import logging
from Network_Mode import StateMachine

from circuitpython_nrf24l01.rf24 import RF24

logging.basicConfig(filename='slave.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

#--- CONFIG ---#
# invalid default values for scoping
SPI_BUS, CSN_PIN, CE_PIN = (None, None, None)

try:
    import spidev

    SPI_BUS = spidev.SpiDev()  # for a faster interface on linux
    CSN_PIN = 0  # use CE0 on default bus (even faster than using any pin)
    CE_PIN = DigitalInOut(board.D23)  # using pin gpio22 (BCM numbering)

except ImportError:  # on CircuitPython only
    # using board.SPI() automatically selects the MCU's
    # available SPI pins, board.SCK, board.MOSI, board.MISO
    SPI_BUS = board.SPI()  # init spi bus object
    CE_PIN = DigitalInOut(board.D4)
    CSN_PIN = DigitalInOut(board.D5)

# GPIO Pins for Leds and Switches Initialized
GPIO.setmode(GPIO.BCM)
TRANSMITTER_LED = 24
RECEIVER_LED = 25
CONNECTION_LED = 12
NM_LED = 16
USB_LED = 21
NM_SWITCH = 3
TXRX_SWITCH = 2
START_SWITCH = 4
GPIO.setup(TRANSMITTER_LED, GPIO.OUT)
GPIO.setup(RECEIVER_LED, GPIO.OUT)
GPIO.setup(CONNECTION_LED, GPIO.OUT)
GPIO.setup(NM_LED, GPIO.OUT)
GPIO.setup(USB_LED, GPIO.OUT)
GPIO.setup(NM_SWITCH, GPIO.IN)
GPIO.setup(TXRX_SWITCH, GPIO.IN)
GPIO.setup(START_SWITCH, GPIO.IN)

# Constants initialized
COMPRESSION_CONFIRMED = b"CompressionConfirmed"
COMPRESSION_ERROR = b"CompressionError"

# initialize the nRF24L01 on the spi bus object
nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)
# On Linux, csn value is a bit coded
#                 0 = bus 0, CE0  # SPI bus 0 is enabled by default
#                10 = bus 1, CE0  # enable SPI bus 2 prior to running this
#                21 = bus 2, CE1  # enable SPI bus 1 prior to running this

# CHANNELS
A = 1
B = 125
C = 75

# Change the Power Amplifier level
nrf.pa_level = 0 # 0, -12, -18
## to enable the custom ACK payload feature
nrf.ack = False  # False disables again
nrf.auto_ack = True
nrf.flush_rx()
nrf.flush_tx()
nrf.arc = 15 #Number of retransmits, default is 3. Int. Value: [0, 15]
# Set channel, from 1 to 125
nrf.channel = B
nrf.data_rate = 250 # RF24_250KBPS (250kbps), RF24_1MBPS (1Mbps), RF24_2MBPS (2Mbps)

# addresses needs to be in a buffer protocol object (bytearray)
address = [b"1Node", b"2Node"]

# set TX address of RX node into the TX pipe
nrf.open_tx_pipe(address[0])  # always uses pipe 0

# set RX address of TX node into an RX pipe
nrf.open_rx_pipe(1, address[1])  # using pipe 1

#--- LEDS ---#
def reset_leds():
    """Turn off all LEDs."""
    GPIO.output(TRANSMITTER_LED, GPIO.LOW)
    GPIO.output(RECEIVER_LED, GPIO.LOW)
    GPIO.output(CONNECTION_LED, GPIO.LOW)
    GPIO.output(NM_LED, GPIO.LOW)
    # GPIO.output(USB_LED, GPIO.LOW)

def blink_success_leds(N, led1, led2):
    for i in range(N):
        GPIO.output(led1, GPIO.HIGH)
        GPIO.output(led2, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(led1, GPIO.LOW)
        GPIO.output(led2, GPIO.LOW)
        time.sleep(0.5)

def blink_failure_leds(N):
    for i in range(N):
        GPIO.output(TRANSMITTER_LED, GPIO.HIGH)
        GPIO.output(RECEIVER_LED, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(TRANSMITTER_LED, GPIO.LOW)
        GPIO.output(RECEIVER_LED, GPIO.LOW)
        time.sleep(0.5)

def blink_usb_LED():
    for i in range(50):
        GPIO.output(USB_LED, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(USB_LED, GPIO.LOW)
        time.sleep(0.05)

#--- SINGLE MODE FUNCTIONS---#
def master(filelist):
    """Function for Master role"""
    decompressed_successfully = False
    counter = 0
    while not decompressed_successfully:
        counter = counter+1
        GPIO.output(TRANSMITTER_LED, GPIO.HIGH)
        nrf.listen = True
        nrf.listen = False

        # Emtpy the FIFOs
        for i in range(10):
            nrf.send(b'hola')
            nrf.read()

        filepath = filelist[0] # Parse the first file in the directory
        # Compress the file using 7z
        os.system(f"yes | 7z a {filepath}.7z {filepath}")
        filepath = filepath + ".7z"

        # This line stores the filename in the message
        message = open(filepath, 'rb').read() + b'separaciofitxer' + bytes(filepath.split('/')[-1], 'utf-8')

        chunks = [message[i:i + 32] for i in range(0, len(message), 32)]

        result = nrf.send(b'Ready')
        # print('fifo state TX1:',fifo_state_tx)
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
        while not sent_successfully:
            sent_successfully = nrf.send(ack_payload)
            time.sleep(0.5)
        print("Last message sent successfully.")
        GPIO.output(CONNECTION_LED, GPIO.LOW)

        # Listen for a new file request (COMPRESSION_CONFIRMED)
        veredict = False
        while not veredict:
            print("Waiting for receiver's veredict...")
            nrf.listen = True
            if nrf.available():
                received_payload = nrf.read()  # Leer el mensaje entrante
                if received_payload == COMPRESSION_CONFIRMED: # If the receiver successfully decompressed the file, exit the loop.
                    # Mensaje transmission complete
                    logging.info("File decompressed successfully.")
                    print("File decompressed successfully.")
                    blink_success_leds(10, CONNECTION_LED, NM_LED)
                    reset_leds()
                    decompressed_successfully = True
                    veredict = True
                elif received_payload == COMPRESSION_ERROR: # If the receiver failed to decompress the file, sent it again.
                    logging.info("The receiver could not decompress the file, retrying...")
                    print("The receiver could not decompress the file, retrying...")
                    if counter == 3:
                        nrf.channel == A
                        counter = 0
                        print("Channel changed to:", nrf.channel)
                    veredict = True

def slave(timeout=1000):
    """"Function for slave role"""
    output = 1
    while output:
        logging.info("Slave function started.")
        nrf.listen = True  # put radio into RX mode and power up
        nrf.flush_tx()
        nrf.flush_rx()  # Vaciar el búfer de recepción
        GPIO.output(RECEIVER_LED, GPIO.HIGH)
        message = []  # list to accumulate message chunks
        start = time.monotonic()
        logging.info("Waiting for start message...")
        print("Waiting for start message...")
        received_payload = nrf.read()  # Leer el mensaje entrante
        while received_payload != b'Ready':
            received_payload = nrf.read()

        logging.info("Waiting for incoming message...")
        print("Waiting for incoming message...")
        message_completed = False
        while not message_completed:
            GPIO.output(CONNECTION_LED, GPIO.LOW)
            if nrf.available():
                received_payload = nrf.read()  # Leer el mensaje entrante
                if received_payload == b'FINALTRANSMISSIO':
                    # Mensaje transmission complete
                    logging.info("Message transmission complete.")
                    print("Message transmission complete.")
                    message_completed = True
                else:
                    # print(f'Received payload: {received_payload}')
                    message.append(received_payload)
                    GPIO.output(CONNECTION_LED, GPIO.HIGH)

                start = time.monotonic()  # Restablecer el temporizador

        # Concatenar y procesar el mensaje completo recibido, si es necesario
        complete_message = b''.join(message)
        print(f"Complete message received: {complete_message}")
        #logging.info(f"Complete message received: {complete_message}")

        filename = complete_message.split(b'separaciofitxer')[-1].decode('utf-8')
        long_desc = len(filename) + len(b'separaciofitxer')
        complete_message = complete_message[:-long_desc]
        print('FILENAME:', filename)
        if filename == "MTP-S24-MRM-C-TX.txt.7z":
            print("1")
            filename_rx = "MTP-S24-MRM-C-RX.txt.7z"
        elif filename == "MTP-S24-SRI-TX.txt.7z":
            print("3")
            filename_rx = "MTP-S24-SRI-RX.txt.7z"
        elif filename == "MTP-S24-NM-TX.txt.7z":
            print("2")
            filename_rx = "MTP-S24-NM-RX.txt.7z"

        with open(filename, 'wb') as file:
            file.write(complete_message)
        # Extract the 7z file
        output = os.system(f"yes | 7z x {filename} -o.")

        if output == 0:
            print("File decompressed successfully, informing the transmitter")
            logging.info("File decompressed successfully, informing the transmitter")

            nrf.listen = False  # put radio in TX mode and power up
            sent_successfully = nrf.send(COMPRESSION_CONFIRMED)
            print("Sent successfully:", sent_successfully)
            logging.info("Sent successfully:", sent_successfully)
            while not sent_successfully:
                print("Error sending the confirmation message, retrying...")
                sent_successfully = nrf.send(COMPRESSION_CONFIRMED)
                time.sleep(0.1)

            blink_success_leds(10, CONNECTION_LED, NM_LED)
            reset_leds()
        else:
            print("Error decompressing the file, informing the transmitter")
            logging.info("Error decompressing the file, informing the transmitter")
            blink_failure_leds(5)

            nrf.listen = False  # put radio in TX mode and power up
            sent_successfully = nrf.send(COMPRESSION_ERROR)
            while not sent_successfully:
                print("Error sending the confirmation message, retrying...")
                sent_successfully = nrf.send(COMPRESSION_ERROR)
                time.sleep(0.1)
            print(f"Soliciting file again. Sent: {sent_successfully}")

    usb_directory = "/media/usb"
    #Delete any existing files in the USB directory
    try:
        files_in_usb = os.listdir(usb_directory)
        for file_name in files_in_usb:
            file_path = os.path.join(usb_directory, file_name)
            os.remove(file_path)
            print(f"Deleted file '{file_name}' from USB directory.")
    except Exception as e:
        print(f"Failed to delete files from USB directory. Error: {e}")

    # Copy the extracted .txt file to the USB directory
    try:
        filename_txt = filename.split(".txt")[0] + ".txt"
        print(f"Copying the message '{filename_txt}' to '/media/usb/'")
        shutil.copy2(filename_txt, "/media/usb/")
        print("Done!")
        blink_usb_LED()
        GPIO.output(USB_LED, GPIO.HIGH)

    except Exception as e:
        print(f"Failed to save the message in '/media/usb'. Error: {e}")



def set_role():
    """Set the role using GPIO switches."""
    # Switch 2 Tx or Rx
    switch_txrx_state = GPIO.input(TXRX_SWITCH)  # Read state of GPIO pin 2
    # Swtich 3 NM or not
    switch_nm_state = GPIO.input(NM_SWITCH)  # Read state of GPIO pin 3
    switch_start_state = GPIO.input(START_SWITCH)

    if switch_nm_state:  # If GPIO pin 3 is on
        print("Network mode selected.")
        print("Switch NM state:", switch_nm_state)
        print("Switch TX/RX state:", switch_txrx_state)
        GPIO.output(NM_LED, GPIO.HIGH)
        sm = StateMachine()
        sm.run()
        return True  # Exit the function
    elif not switch_nm_state and switch_txrx_state:  # If GPIO pin 3 is off and GPIO pin 2 is on
        GPIO.output(NM_LED, GPIO.LOW)
        print("Transmitter role selected.")
        print("Switch NM state:", switch_nm_state)
        print("Switch TX/RX state:", switch_txrx_state)
        # set TX address of RX node into the TX pipe
        nrf.open_tx_pipe(address[0])  # always uses pipe 0
        # set RX address of TX node into an RX pipe
        nrf.open_rx_pipe(1, address[1])  # using pipe 1
        path = '/media/usb'  # Ruta completa al archivo en el directorio /mnt/usbdrive
        filelist = np.array([os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]) # Get the list of files in the directory
        filelist = filelist[np.where([x.endswith(".txt") and not x.startswith(".") for x in filelist])[0]] # Get the elements that end with ".txt" and does not start with "."
        print("filelist",filelist)
        if not os.path.exists(path):
            print(f"Path not found: {path}")
            return True
        if len(filelist) == 0:
            print(f"No files in: {path}")
            return True
        master(filelist)
        reset_leds()
        GPIO.output(USB_LED, GPIO.LOW)
        return True
    else:  # If neither GPIO pin 2 nor GPIO pin 3 is on
        GPIO.output(NM_LED, GPIO.LOW)
        print("Receiver role selected.")
        print("Switch NM state:", switch_nm_state)
        print("Switch TXRX state:", switch_txrx_state)
        # set TX address of RX node into the TX pipe
        nrf.open_tx_pipe(address[1])  # always uses pipe 1
        # set RX address of TX node into an RX pipe
        nrf.open_rx_pipe(1, address[0])  # using pipe 0
        slave()
        reset_leds()
        GPIO.output(USB_LED, GPIO.LOW)
        return True

#--- MAIN ---#
if __name__ == "__main__":
    reset_leds()
    GPIO.output(USB_LED, GPIO.LOW)
    print("Waiting for USB drive...")
    num_devices = 0
    while num_devices < 2:
        df = subprocess.check_output("lsusb")
        df = df.split(b'\n')
        num_devices = len(df)-1
        time.sleep(1)
    print("USB unit connected")
    GPIO.output(USB_LED, GPIO.HIGH)
    print("Waiting for start switch...")
    start = False
    start_switch = GPIO.input(START_SWITCH)
    print("Switch start state:", start_switch)
    while not start:
        print("Switch start state:", start_switch)
        if start_switch:
            start = True
        time.sleep(0.1)
        start_switch = GPIO.input(START_SWITCH)
    try:
        set_role()
        time.sleep(5)
        # reset_leds()
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
        GPIO.cleanup()
        reset_leds()
else:
    print("    Run slave() on receiver\n    Run master() on transmitter")
