import time
import struct
import board
from digitalio import DigitalInOut
import os
import subprocess
import RPi.GPIO as GPIO
import threading
import numpy as np

from circuitpython_nrf24l01.rf24 import RF24

# invalid default values for scoping
SPI_BUS, CSN_PIN, CE_PIN = (None, None, None)

try:  # on Linux
    import spidev

    SPI_BUS = spidev.SpiDev()  # for a faster interface on linux
    CSN_PIN = 0  # use CE0 on default bus (even faster than using any pin)
    CE_PIN = DigitalInOut(board.D23)  # using pin gpio22 (BCM numbering)

except ImportError:  # on CircuitPython only
    # using board.SPI() automatically selects the MCU's
    # available SPI pins, board.SCK, board.MOSI, board.MISO
    SPI_BUS = board.SPI()  # init spi bus object

    # change these (digital output) pins accordingly
    CE_PIN = DigitalInOut(board.D4)
    CSN_PIN = DigitalInOut(board.D5)

# Initialize the leds
GPIO.setmode(GPIO.BCM)
# I CREATED VARIABLES FOR EASY READING
TRANSMITTER_LED = 24
RECEIVER_LED = 25
CONNECTION_LED = 12
NM_LED = 16
USB_LED = 21
NM_SWITCH = 3
TXRX_SWITCH = 2
GPIO.setup(TRANSMITTER_LED, GPIO.OUT)
GPIO.setup(RECEIVER_LED, GPIO.OUT)
GPIO.setup(CONNECTION_LED, GPIO.OUT)
GPIO.setup(NM_LED, GPIO.OUT)
GPIO.setup(USB_LED, GPIO.OUT)
GPIO.setup(NM_SWITCH, GPIO.IN)
GPIO.setup(TXRX_SWITCH, GPIO.IN)

# initialize the nRF24L01 on the spi bus object
nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)
# On Linux, csn value is a bit coded
#                 0 = bus 0, CE0  # SPI bus 0 is enabled by default
#                10 = bus 1, CE0  # enable SPI bus 2 prior to running this
#                21 = bus 2, CE1  # enable SPI bus 1 prior to running this

# Change the Power Amplifier level
nrf.pa_level = 0 # 0, -12, -18
## to enable the custom ACK payload feature
nrf.ack = False  # False disables again
# Set channel, from 1 to 125
nrf.channel = 1
nrf.data_rate = 250 # RF24_250KBPS (250kbps), RF24_1MBPS (1Mbps), RF24_2MBPS (2Mbps)

# addresses needs to be in a buffer protocol object (bytearray)
address = [b"1Node", b"2Node"]

# to use different addresses on a pair of radios, we need a variable to
# uniquely identify which address this radio will use to transmit
# 0 uses address[0] to transmit, 1 uses address[1] to transmit
'''
radio_number = bool(
    int(input("Which radio is this? Enter '0' or '1'. Defaults to '0' ") or 0)
)
'''

<<<<<<< HEAD
=======
# set TX address of RX node into the TX pipe
nrf.open_tx_pipe(address[0])  # always uses pipe 0

# set RX address of TX node into an RX pipe
nrf.open_rx_pipe(1, address[1])  # using pipe 1

def USB_led():
    while True:
        df = subprocess.check_output("lsusb")
        df = df.split(b'\n')
        num_devices = len(df)-1
        if num_devices < 2:
            GPIO.output(USB_LED, GPIO.LOW)
            time.sleep(0.5)
        else:
            GPIO.output(USB_LED, GPIO.HIGH)
            time.sleep(0.5)
        
def blink_led():
    delay = 0.2
    while True:
        """Blink a LED."""
        GPIO.output(CONNECTION_LED, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(CONNECTION_LED, GPIO.LOW)
        time.sleep(delay)

def reset_leds():
    """Turn off all LEDs."""
    GPIO.output(TRANSMITTER_LED, GPIO.LOW)
    GPIO.output(RECEIVER_LED, GPIO.LOW)
    GPIO.output(CONNECTION_LED, GPIO.LOW)
    GPIO.output(NM_LED, GPIO.LOW)
    GPIO.output(USB_LED, GPIO.LOW)


def master(filelist, count=5):
    nrf.listen = False  # ensure the nRF24L01 is in TX mode
    GPIO.output(TRANSMITTER_LED, GPIO.HIGH)
    
    filepath = filelist[0]
    
    print(f"Sending file: {filepath}")
    
    # # Compress the file using zip
    # os.system(f"zip -j {filepath}.zip {filepath}")
    # filepath = filepath + ".zip"
    
    # Compress the file using 7z
    os.system(f"yes | 7z a {filepath}.7z {filepath}")
    filepath = filepath + ".7z"
    
    # This line stores the filename in the message
    message = open(filepath, 'rb').read() + b'separaciofitxer' + bytes(filepath.split('/')[-1], 'utf-8')

    chunks = [message[i:i + 32] for i in range(0, len(message), 32)]

    retries = 0
    # Start the LED blink thread
    thread_blink_led = threading.Thread(target=blink_led)
    thread_blink_led.start() 
    for chunk in chunks:
        # Show percentage of message sent
        print(f"Percentage of message sent: {round((chunks.index(chunk)+1)/len(chunks)*100, 2)}%")
        # Append the packet ID to the end of the chunk
        # chunk = chunk + bytes([packet_ID])
        # print(f"Sending chunk: {chunk}")
        # print("Length of chunk:", len(chunk))
        result = nrf.send(chunk)  # Enviar el chunk

        # received_payload = nrf.read()  # Leer el payload recibido
        if result:  # Si se recibe el ACK esperado
            print("ACK received. Sending next chunk.")
            retries = 0
        else:
            print("No ACK received. Retrying...")
            while not result:
                result = nrf.send(chunk)
                print(result)
                time.sleep(0.5)
                # retries += 1
                # if retries > 100:
                #     print("Too many retries. Exiting...")
                #     reset_leds()
                #     break

        # if attempt < count - 1:  # Si no se recibió el ACK, reintento
        #     print("No ACK received. Retrying...")
        #     nrf.resend

    print("Message transmission complete.")
    ack_payload = b'FINALTRANSMISSIO'  # Mensaje de finalización
    nrf.listen = False  # Dejar de escuchar para poder enviar
    sent_successfully = nrf.send(ack_payload)  # Enviar el mensaje de confirmación
    if sent_successfully:
        print("Confirmation message sent successfully.")
    else:
        print("Failed to send confirmation message.")
        nrf.send(ack_payload)
    # Kill blink thread
    thread_blink_led.join()
    GPIO.output(TRANSMITTER_LED, GPIO.LOW)


def slave(timeout=1000):
    nrf.listen = True  # put radio into RX mode and power up
    GPIO.output(RECEIVER_LED, GPIO.HIGH)
    message = []  # list to accumulate message chunks
    start = time.monotonic()

    print("Waiting for incoming message...")
    # Start the LED blink thread
    thread_blink_led = threading.Thread(target=blink_led)
    thread_blink_led.start() 
    while (time.monotonic() - start) < timeout:
        if nrf.available():
            received_payload = nrf.read()  # Leer el mensaje entrante
            if received_payload == b'FINALTRANSMISSIO':
                # Mensaje transmission complete
                print("Message transmission complete.")
                break
            else:
                # print(f'Received payload: {received_payload}')
                message.append(received_payload)

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
    
    # # # Extract the zip file
    # # os.system(f"unzip -j {filename} -d .")
    
    # Extract the 7z file
    os.system(f"yes | 7z x {filename} -o.")

    print("Received message stored in",filename)
    # Kill blink thread
    thread_blink_led.join()
    GPIO.output(RECEIVER_LED, GPIO.LOW)

    # Guardar también el mensaje completo en un archivo en /mnt/usbdrive
    try:
        with open('/media/usb/'+filename, 'wb') as file:
            file.write(complete_message)
            # # # Extract the zip file
            # # os.system(f"unzip -j /media/usb/{filename} -d /media/usb/")
            # Extract the 7z file
            os.system(f"yes | 7z x /media/usb/{filename} -o/media/usb/")
        print("Received message also stored in '/media/usb/'",filename)
    except Exception as e:
        print(f"Failed to save the message in '/media/usb'. Error: {e}")
   # nrf.listen = False  # Se recomienda mantener el transceptor en modo TX mientras está inactivo


''' OLD SET_ROLE 
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
        path = '/media/usb'  # Ruta completa al archivo en el directorio /mnt/usbdrive
        filelist = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        if not os.path.exists(path):
            print(f"Path not found: {path}")
            return True
        if len(filelist) == 0:
            print(f"No files in: {path}")
            return True
        master(filelist)
        return True
    elif role == 'Q':
        nrf.power = False
        return False
    else:
        print(role, "is an unrecognized input. Please try again.")
        return set_role()
'''

def set_role(): 
    """Set the role using GPIO switches."""
    # Switch 2 Tx or Rx
    switch_txrx_state = GPIO.input(TXRX_SWITCH)  # Read state of GPIO pin 2
    # Swtich 3 NM or not
    switch_nm_state = GPIO.input(NM_SWITCH)  # Read state of GPIO pin 3
    
    if switch_nm_state:  # If GPIO pin 3 is on
        print("Network mode selected.")
        print("Switch NM state:", switch_nm_state)
        print("Switch TXRX state:", switch_txrx_state)
        GPIO.output(NM_LED, GPIO.HIGH)
        return False  # Exit the function
    elif not switch_nm_state and switch_txrx_state:  # If GPIO pin 3 is off and GPIO pin 2 is on
        GPIO.output(NM_LED, GPIO.LOW)
        print("Transmitter role selected.")
        print("Switch NM state:", switch_nm_state)
        print("Switch TX state:", switch_txrx_state)
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
        return True

# Canviar l'ordre, primer espera al primer switch per si es network mode o no, després si NO es 
# Network Mode 
if __name__ == "__main__":
    print("Waiting for USB drive...")
    # Start the USB LED thread
    t = threading.Thread(target=USB_led)
    t.start()
    num_devices = 0
    while num_devices < 2:
        df = subprocess.check_output("lsusb")
        df = df.split(b'\n')
        num_devices = len(df)-1
        time.sleep(1)
    print("USB unit connected")
    # # Assumeixo que aquí ja ha trobat el USB
    # GPIO.output(USB_LED, GPIO.HIGH)    
    try:
        set_role()
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
        GPIO.cleanup()
        reset_leds()
else:
    print("    Run slave() on receiver\n    Run master() on transmitter")
