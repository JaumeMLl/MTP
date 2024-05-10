import time
import board
from digitalio import DigitalInOut
import os
import subprocess
import RPi.GPIO as GPIO
import numpy as np
import shutil
import logging

# some_file.py
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.append("/home/pi/MTP/")
print(sys.path)

from circuitpython_nrf24l01.rf24 import RF24

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

nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)

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
#nrf = RF24(SPI_BUS, CSN_PIN, CE_PIN)
# On Linux, csn value is a bit coded
#                 0 = bus 0, CE0  # SPI bus 0 is enabled by default
#                10 = bus 1, CE0  # enable SPI bus 2 prior to running this
#                21 = bus 2, CE1  # enable SPI bus 1 prior to running this
