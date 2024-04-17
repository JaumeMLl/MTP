import struct
import zlib
import time
import board
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

def read_file(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

def master(compressed_data, count=5, timeout=500):
    nrf.listen = False


    # Ajusta este valor si es necesario, según la eficiencia de compresión esperada
    chunk_size = 30
    chunks = [compressed_data[i:i + chunk_size] for i in range(0, len(compressed_data), chunk_size)]

    for chunk_number, chunk in enumerate(chunks):
        sequence_byte = struct.pack('B', chunk_number % 256)
        checksum = calculate_checksum(chunk)
        chunk_with_metadata = sequence_byte + chunk + struct.pack('B', checksum)

        print(f"Fragmento {chunk_number + 1} (comprimido y con metadata):", chunk_with_metadata)
        if len(chunk_with_metadata) > 32:
            print(f"El fragmento comprimido {chunk_number + 1} excede el límite de tamaño.")
            continue

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
                    start_time = time.monotonic()  # Restablece el temporizador tras recibir y verificar correctamente
                else:
                    print(f"Error de checksum en el fragmento {sequence}.")

            except zlib.error as e:
                print(f"Error descomprimiendo el fragmento {sequence}: {e}")
                # No envía ACK si hay un error de descompresión

    nrf.listen = False  # Cambia a modo TX tras completar la recepción


def set_role():
    role = input("Which radio is this? Enter '0' for sender, '1' for receiver: ").strip()
    if role == '0':
        filepath = "mtp.txt"
        data = read_file(filepath)
        print(f"Original size: {len(data)} bytes.")
        compressed_data = compress_data(data)
        print(f"Compressed size: {len(compressed_data)} bytes.")
        master(compressed_data)  # Asumiendo que master ahora acepta datos binarios comprimidos directamente
    elif role == '1':
        slave()
    else:
        print("Invalid role selected. Please enter '0' or '1'.")

if __name__ == "__main__":
    set_role()
