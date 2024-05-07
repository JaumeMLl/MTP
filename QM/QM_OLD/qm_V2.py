import time
import struct
import board
from digitalio import DigitalInOut
import os
<<<<<<< HEAD
import subprocess
=======
>>>>>>> 0ee453c5ed5b5a67ecded36ce51ef372dba4969e

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


# initialize the nRF24L01 on the spi bus object
nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)
# On Linux, csn value is a bit coded
#                 0 = bus 0, CE0  # SPI bus 0 is enabled by default
#                10 = bus 1, CE0  # enable SPI bus 2 prior to running this
#                21 = bus 2, CE1  # enable SPI bus 1 prior to running this

# Change the Power Amplifier level
nrf.pa_level = 0
## to enable the custom ACK payload feature
nrf.ack = False  # False disables again
nrf.auto_ack = True

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

<<<<<<< HEAD
def master(filelist, count=5):
    nrf.listen = False  # ensure the nRF24L01 is in TX mode

    #with open(filepath, 'r') as file:
    #    message = file.read().encode()
    
    ## TODO: fix this. It is not working
    # message = b''
    # for filepath in filelist:
    #     file = open(filepath,'rb')
    #     message += file.read()
    
    filepath = filelist[0]
    # This line stores the filename in the message
    message = open(filepath, 'rb').read() + b'separaciofitxer' + bytes(filepath.split('/')[-1], 'utf-8')
=======
def master(filepath, count=5):
    nrf.listen = False  # ensure the nRF24L01 is in TX mode

    with open(filepath, 'r') as file:
        message = file.read().encode()
>>>>>>> 0ee453c5ed5b5a67ecded36ce51ef372dba4969e

    while True:
        chunks = [message[i:i + 32] for i in range(0, len(message), 32)]
        
        for chunk in chunks:
            result = nrf.send(chunk)  # Enviar el chunk
            # received_payload = nrf.read()  # Leer el payload recibido
            if result:  # Si se recibe el ACK esperado
                print("ACK received. Sending next chunk.")
            else:
                while not result:
                    print("No ACK received. Retrying...")
                    result = nrf.send(chunk)
    
            # Show percentage of message sent
            print(f"Percentage of message sent: {round((chunks.index(chunk)+1)/len(chunks)*100, 2)}%")
        
        print("Message transmission complete.")
        ack_payload = b'FINALTRANSMISSIO'  # Mensaje de finalización
        nrf.listen = False  # Dejar de escuchar para poder enviar
        sent_successfully = nrf.send(ack_payload)  # Enviar el mensaje de confirmación
        if sent_successfully:
            print("Confirmation message sent successfully.")
        else:
    #aqui es el unico sitio donde se podria hacer retransmi sin liarla demasiado
            sent_successfully = nrf.send(ack_payload)
            while not sent_successfully:
                sent_successfully = nrf.send(ack_payload)
            print("Confirmation message sent successfully.")

def slave(timeout=6):
    nrf.listen = True  # put radio into RX mode and power up

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
<<<<<<< HEAD
    complete_message = b''.join(message)
    print(f"Complete message received: {complete_message}")

    # Opcional: Guardar el mensaje completo en un archivo
    filename = complete_message.split(b'separaciofitxer')[-1].decode('utf-8')
    long_desc = len(filename) + len(b'separaciofitxer')
    complete_message = complete_message[:-long_desc]
    with open(filename, 'wb') as file:
        file.write(complete_message)

    print("Received message stored in",filename)

    # Guardar también el mensaje completo en un archivo en /mnt/usbdrive
    try:
        with open('/media/usb/'+filename, 'wb') as file:
            file.write(complete_message)
        print("Received message also stored in '/media/usb/'",filename)
    except Exception as e:
        print(f"Failed to save the message in '/media/usb'. Error: {e}")
=======
    complete_message = b''.join(message).decode('utf-8')
    print(f"Complete message received: {complete_message}")

    # Opcional: Guardar el mensaje completo en un archivo
    with open('received_message.txt', 'w') as file:
        file.write(complete_message)

    print("Received message stored in 'received_message.txt'")

    # Guardar también el mensaje completo en un archivo en /mnt/usbdrive
    try:
        with open('/mnt/usbdrive/received_message.txt', 'w') as file:
            file.write(complete_message)
        print("Received message also stored in '/mnt/usbdrive/received_message.txt'")
    except Exception as e:
        print(f"Failed to save the message in '/mnt/usbdrive'. Error: {e}")
>>>>>>> 0ee453c5ed5b5a67ecded36ce51ef372dba4969e
    nrf.listen = False  # Se recomienda mantener el transceptor en modo TX mientras está inactivo



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
<<<<<<< HEAD
        path = '/media/usb'  # Ruta completa al archivo en el directorio /mnt/usbdrive
        filelist = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        if not os.path.exists(path):
            print(f"Path not found: {path}")
            return True
        if len(filelist) == 0:
            print(f"No files in: {path}")
            return True
        master(filelist)
=======
        filepath = '/mnt/usbdrive/mtp.txt'  # Ruta completa al archivo en el directorio /mnt/usbdrive
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return True
        master(filepath)
>>>>>>> 0ee453c5ed5b5a67ecded36ce51ef372dba4969e
        return True
    elif role == 'Q':
        nrf.power = False
        return False
    else:
        print(role, "is an unrecognized input. Please try again.")
        return set_role()

if __name__ == "__main__":
<<<<<<< HEAD
    print("Waiting for USB drive...")
    num_devices = 0
    while num_devices < 2:
        df = subprocess.check_output("lsusb")
        df = df.split(b'\n')
        num_devices = len(df)-1
        time.sleep(1)
    print("USB unit connected")
=======
>>>>>>> 0ee453c5ed5b5a67ecded36ce51ef372dba4969e
    try:
        while set_role():
            pass  # continue example until 'Q' is entered
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
else:
    print("    Run slave() on receiver\n    Run master() on transmitter")
