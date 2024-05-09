import RPi.GPIO as GPIO
import time
import os

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

def USB_led():
   # Check number of files in the USB drive
    while True:
        num_devices = len(os.listdir('/dev/bus/usb'))  # Checking USB devices
        if num_devices >= 1:    # 1 !!
            GPIO.output(USB_LED, GPIO.HIGH)
            time.sleep(0.5)
            break
        else:
            GPIO.output(USB_LED, GPIO.LOW)
            time.sleep(0.5)