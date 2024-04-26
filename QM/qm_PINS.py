import time
import struct
import board
from digitalio import DigitalInOut
import os
import subprocess
import RPi.GPIO as GPIO

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

#Cleanup per reiniciar
GPIO.cleanup()
# Initialize the leds
GPIO.setmode(GPIO.BCM)
# I CREATED VARIABLES FOR EASY READING
TRANSMITTER_LED = 24
RECEIVER_LED = 25
CONNECTION_LED = 12
NM_LED = 16
USB_LED = 21
NM_SWITCH = 2
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
nrf.pa_level = -12
## to enable the custom ACK payload feature
nrf.ack = True  # False disables again
# Set channel, from 1 to 125
# nrf.setChannel(80)

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

# set TX address of RX node into the TX pipe
nrf.open_tx_pipe(address[0])  # always uses pipe 0

# set RX address of TX node into an RX pipe
nrf.open_rx_pipe(1, address[1])  # using pipe 1

def master(filelist, count=5):
    nrf.listen = False  # ensure the nRF24L01 is in TX mode
    GPIO.output(TRANSMITTER_LED, GPIO.HIGH)

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
    GPIO.output(TRANSMITTER_LED, GPIO.LOW)


def slave(timeout=6):
    nrf.listen = True  # put radio into RX mode and power up
    GPIO.output(RECEIVER_LED, GPIO.HIGH)
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
    GPIO.output(RECEIVER_LED, GPIO.LOW)

    # Guardar también el mensaje completo en un archivo en /mnt/usbdrive
    try:
        with open('/media/usb/'+filename, 'wb') as file:
            file.write(complete_message)
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
        GPIO.output(NM_LED, GPIO.HIGH)
        return False  # Exit the function
    elif not switch_nm_state and switch_txrx_state:  # If GPIO pin 3 is off and GPIO pin 2 is on
        print("Transmitter role selected.")
        print("Switch NM state:", switch_nm_state)
        print("Switch TXRX state:", switch_txrx_state)
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
    else:  # If neither GPIO pin 2 nor GPIO pin 3 is on
        print("Receiver role selected.")
        slave()
        return True

# Canviar l'ordre, primer espera al primer switch per si es network mode o no, després si NO es 
# Network Mode 
if __name__ == "__main__":
    print("Waiting for USB drive...")
    num_devices = 0
    while num_devices < 2:
        df = subprocess.check_output("lsusb")
        df = df.split(b'\n')
        num_devices = len(df)-1
        time.sleep(1)
    print("USB unit connected")
    # Assumeixo que aquí ja ha trobat el USB
    GPIO.output(USB_LED, GPIO.HIGH)    
    try:
        while set_role():
            pass  # continue example until 'Q' is entered
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
        GPIO.cleanup()
else:
    print("    Run slave() on receiver\n    Run master() on transmitter")
