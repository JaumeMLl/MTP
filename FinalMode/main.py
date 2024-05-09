import time
import board
from digitalio import DigitalInOut
import os
import subprocess
import RPi.GPIO as GPIO
import numpy as np
import shutil
import logging

from circuitpython_nrf24l01.rf24 import RF24

from NetworkMode.CommsMethods import *
from NetworkMode.Constants_Network_Mode import *
from NetworkMode.Network_Mode import *
from Single_Mode.Single_Mode import *
from config import *

#-- SET ROLE --#

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
        while True:
            # Ejecuta el script externo
            subprocess.run(['python3', 'Network_Mode.py'])
            print("FILE ENDED, REPEATING....")
            # Pausa entre ejecuciones, si es necesario
            time.sleep(1)  # Pausa de 1 segundo
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
    except KeyboardInterrupt:
        print(" Keyboard Interrupt detected. Powering down radio...")
        nrf.power = False
        GPIO.cleanup()
        reset_leds()
else:
    print("    Run slave() on receiver\n    Run master() on transmitter")