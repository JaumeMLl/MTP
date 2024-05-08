import subprocess
import time

while True:
    # Ejecuta el script externo
    subprocess.run(['python3', 'Network_Mode.py'])
    print("FILE ENDED, REPEATING....")
    # Pausa entre ejecuciones, si es necesario
    time.sleep(1)  # Pausa de 1 segundo