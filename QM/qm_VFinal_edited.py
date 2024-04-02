import struct
import zlib
import time
import board
import subprocess
import chardet
import os
from digitalio import DigitalInOut
from circuitpython_nrf24l01.rf24 import RF24


# Configuración inicial del SPI y pines para nRF24L01+
try:
    import spidev
    SPI_BUS = spidev.SpiDev()
    CSN_PIN = 0
    CE_PIN = DigitalInOut(board.D22)
except ImportError:
    SPI_BUS = board.SPI()
    CE_PIN = DigitalInOut(board.D4)
    CSN_PIN = DigitalInOut(board.D5)

nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)
nrf.pa_level = -12

address = [b"1Node", b"2Node"]
radio_number = bool(int(input("Which radio is this? Enter '0' or '1'. Defaults to '0' ") or 0))
nrf.open_tx_pipe(address[radio_number])
nrf.open_rx_pipe(1, address[not radio_number])

def calculate_checksum(data):
    return sum(data) & 0xFF

def compress_data(data):
    return zlib.compress(data)

# Read file with unknwon encoding
def read_file(path):
    try: 
        # We first detect the encoding of the file
        with open(path, 'rb') as file_raw: 
            rawdata = file_raw.read(64)
            result = chardet.detect(rawdata)
            encoding = result['encoding']

        # Then we decode the file with the known encoding
        with open(path, 'r', encoding = encoding) as file: 
            content = file.read(64)
            print(f"Successfully read with encoding: {encoding}")
            return content
        
    # Possible errors
    except UnicodeDecodeError:
        print(f"Failed with encoding: {encoding}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None

# Get path from USB
def get_path():
    rpistr = "/media/mtp/"
    proc = subprocess.Popen(["ls", rpistr], stdout=subprocess.PIPE)
    line = proc.stdout.readline().decode("utf-8").strip()
    path = rpistr + line + "/"
    return path

# Write protocol
def write_protocol(received_data):
    # Get the path to the USB drive
    usb_path = get_path()
    # Check if the USB drive is mounted
    if os.path.exists(usb_path):
        # Specify the filename
        new_file = os.path.join(usb_path, 'received.txt')
        with open(new_file, 'w') as file: 
            file.write(received_data)
    else:
        print("USB drive not found.")


def master(compressed_data, count=5, timeout=500):
    nrf.listen = False # Tx

    # Adjust the value to compression efficiency
    chunk_size = 30
    chunks = [compressed_data[i:i + chunk_size] for i in range(0, len(compressed_data), chunk_size)]

    # Compression
    for chunk_number, chunk in enumerate(chunks):
        sequence_byte = struct.pack('B', chunk_number % 256)
        checksum = calculate_checksum(chunk)
        chunk_with_metadata = sequence_byte + chunk + struct.pack('B', checksum)

        print(f"Fragmento {chunk_number + 1} (comprimido y con metadata):", chunk_with_metadata)
        if len(chunk_with_metadata) > 32:
            print(f"El fragmento comprimido {chunk_number + 1} excede el límite de tamaño.")
            continue
        
        # Sending, count attemps to send each chunck
        print(f"Enviando fragmento {chunk_number + 1}/{len(chunks)}")
        attempt = 0
        while attempt < count:
            nrf.send(chunk_with_metadata)
            if not nrf.send(chunk_with_metadata):
                print(f"Error al enviar el fragmento {chunk_number + 1}, reintentando...")
                attempt += 1
            else:
                print(f"Fragmento {chunk_number + 1} enviado con éxito.")
                break

        if attempt == count:
            print("Error al enviar después de varios intentos.")
            break

        time.sleep(0.1)


def slave(timeout=6):
    nrf.listen = True  # Radio en modo RX para recibir datos
    start_time = time.monotonic()  # Captura el tiempo inicial
    received_data = ''

    while time.monotonic() - start_time < timeout:
        if nrf.available():
            received_payload = nrf.read()  # Lee el fragmento recibido
            sequence, *data, received_checksum = struct.unpack('B' * len(received_payload), received_payload)
            data_bytes = bytes(data)

            try:
                # Intenta descomprimir el fragmento
                decompressed_data = zlib.decompress(data_bytes[:-1])  # Excluye el byte del checksum para descomprimir
                # Calcula el checksum del fragmento descomprimido para verificación
                calculated_checksum = calculate_checksum(data_bytes[:-1])

                if calculated_checksum == received_checksum:
                    print(f"Fragmento {sequence} descomprimido y verificado correctamente.")
                    # Envía ACK si la descompresión y verificación son exitosas
                    nrf.send(b'ACK')
                    # Saves data in received_data string
                    received_data += decompressed_data
                    start_time = time.monotonic()  # Restablece el temporizador tras recibir y verificar correctamente
                else:
                    print(f"Error de checksum en el fragmento {sequence}.")

            except zlib.error as e:
                print(f"Error descomprimiendo el fragmento {sequence}: {e}")
                # No envía ACK si hay un error de descompresión

    nrf.listen = False  # Cambia a modo TX tras completar la recepción
    return received_data


def set_role():
    role = input("Which radio is this? Enter '0' for sender, '1' for receiver: ").strip()
    if role == '0':
        # Read 
        path = get_path()
        data = read_file(path)
        print(f"Original size: {len(data)} bytes.")
        # Compression
        compressed_data = compress_data(data)
        print(f"Compressed size: {len(compressed_data)} bytes.")
        # Send (assuming master accepts compressed data already)
        master(compressed_data)  
    elif role == '1':
        # Receive
        received_data = slave()
        # Write 
        write_protocol(received_data)
        
    else:
        print("Invalid role selected. Please enter '0' or '1'.")

if __name__ == "__main__":
    set_role()
