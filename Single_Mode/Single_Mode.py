import time
import struct
import board
from digitalio import DigitalInOut
import os
import subprocess
import RPi.GPIO as GPIO
import threading
import numpy as np
import shutil


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
        
def reset_leds():
    """Turn off all LEDs."""
    GPIO.output(TRANSMITTER_LED, GPIO.LOW)
    GPIO.output(RECEIVER_LED, GPIO.LOW)
    GPIO.output(CONNECTION_LED, GPIO.LOW)
    GPIO.output(NM_LED, GPIO.LOW)
    GPIO.output(USB_LED, GPIO.LOW)

def blink_success_leds(N):
    for i in range(N):
        GPIO.output(CONNECTION_LED, GPIO.HIGH)
        GPIO.output(NM_LED, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(CONNECTION_LED, GPIO.LOW)
        GPIO.output(NM_LED, GPIO.LOW)
        time.sleep(0.5)

def blink_failure_leds(N):
    for i in range(N):
        GPIO.output(TRANSMITTER_LED, GPIO.HIGH)
        GPIO.output(RECEIVER_LED, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(TRANSMITTER_LED, GPIO.LOW)
        GPIO.output(RECEIVER_LED, GPIO.LOW)
        time.sleep(0.5)

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
    canal = nrf.send(b'canal')
    while not canal:
        canal = nrf.send(b'canal')
        print('hola canal')
    result = False
    for i, chunk in enumerate(chunks):
        print('NUMERO', i)
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
        blink_success_leds(10)
    else:
        print("Failed to send confirmation message.")
        sent_successfully = nrf.send(ack_payload)
        while not sent_successfully:
            sent_successfully = nrf.send(ack_payload)
            time.sleep(0.5)
        print("Confirmation message sent successfully.")
        GPIO.output(CONNECTION_LED, GPIO.LOW)



def slave(timeout=1000):
    nrf.listen = True  # put radio into RX mode and power up
    GPIO.output(RECEIVER_LED, GPIO.HIGH)
    message = []  # list to accumulate message chunks
    start = time.monotonic()

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
        blink_success_leds(10)
    else:
        print("Error decompressing the file")
        blink_failure_leds(10)

    # Buscar los archivos .txt en el directorio de trabajo
    txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]

    print("Received message stored in",txt_files)
    

    # Copy the extracted .txt file to the USB directory
    try:
        for txt_file in txt_files:
            shutil.copy(txt_file, '/media/usb/')
            print(f"Received message '{txt_file}' also stored in '/media/usb/'")
    except Exception as e:
        print(f"Failed to save the message in '/media/usb'. Error: {e}")



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
 
    try:
        set_role()
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
        GPIO.cleanup()
        reset_leds()
else:
    print("    Run slave() on receiver\n    Run master() on transmitter")