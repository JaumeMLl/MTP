from asyncio import sleep
import random
import time
import os
import numpy as np

import struct
import board
from digitalio import DigitalInOut
import subprocess

from CommsMethods import *
from Constants_Network_Mode import *

from circuitpython_nrf24l01.rf24 import RF24

#---- CONFIG ----#

# invalid default values for scoping
SPI_BUS, CSN_PIN, CE_PIN = (None, None, None)

try:  # on Linux
    import spidev

    SPI_BUS = spidev.SpiDev()  # for a faster interface on linux
    CSN_PIN = 0  # use CE0 on default bus (even faster than using any pin)
    CE_PIN = DigitalInOut(board.D23)  # using pin gpio23 (BCM numbering)

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
nrf.pa_level = -18
## to enable the custom ACK payload feature
nrf.ack = False  # False disables again
nrf.auto_ack = True
nrf.data_rate = 2 #Bit rate of: 2 (Mbps), 1 (Mbps), 250 (kbps); Insert value
nrf.arc = 15 #Number of retransmits, default is 3. Int. Value: [0, 15]
nrf.ard = 1500 #Retransmission time from [250, 4000] in microseconds
nrf.crc = 2 #Default 2. Number of bytes for the CRC. Int. Value: [0, 2]

# set TX address of RX node into the TX pipe
nrf.open_tx_pipe(BROADCAST_ID)

# set RX address of TX node into an RX pipe
nrf.open_rx_pipe(1, BROADCAST_ID)

#---- CLASSES ----#
class CommsInfo:
    def __init__(self, listening_pipe_address, destination_pipe_address, channel):
        """
        Initializes communication information.
        
        Parameters:
        - rxId: The ID of the receiving device.
        - myId: The ID of this device.
        - channel: The communication channel.
        """
        self.listening_pipe_address = listening_pipe_address
        self.destination_pipe_address = destination_pipe_address
        self.channel = channel
    
    def __str__(self):
        return f"Listening Pipe: '{self.listening_pipe_address}', " \
               f"Destination Pipe: '{self.destination_pipe_address}', " \
               f"Channel: '{self.channel}'"

#---- VARIABLES GLOBALES ----#
comms_info = CommsInfo(BROADCAST_ID, BROADCAST_ID, CHANNEL1)

#---- FUNCTIONS ----#

def checkFileExists():
    """
    Checks if a file exists in the specified directory.
    
    Returns:
    - True if the file exists, False otherwise.
    """
    path = FOLDER_PATH  # Ruta completa al archivo en el directorio donde se monta el USB
    filelist = np.array([os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]) # Get the list of files in the directory
    filelist = filelist[np.where([x.endswith(".txt") and not x.startswith(".") for x in filelist])[0]] # Get the elements that end with ".txt" and does not start with "."
    if not os.path.exists(path):
        print(f"Path not found: {path}")
        return False
    if len(filelist) == 0:
        print(f"No files in: {path}")
        return False
    print("File Found")
    return True

def ledOn():
    """
    Simulates turning on an LED (for demonstration purposes).
    """
    # TODO implement this function
    print("Turning LED on...")

def anySupplicant():
    """
    Checks for any supplicant device in the communication channel.
    
    Waits for a File Request Message. (<- FILE_REQUEST_MSG )

    Actualize the value of the comms_info.destination_pipe_address with the adress of the transmitter.
    
    Parameters:
    - comms_info: Communication information object.

    Returns:
    - True if FileRequestMesg is received, False otherwise.
    """

    return wait_for_desired_message(comms_info, FILE_REQUEST_MSG, TIMEOUT, nrf)

def sendRequestAcc():
    """
    Sends a request acceptance message to a requesting device. (-> REQUEST_ACC_MSG)
    
    Parameters:
    - comms_info: Communication information object.
    """
    # Preparar y enviar un mensaje de confirmación de vuelta al transmisor
    time.sleep(random.randint(0, REQUEST_ACC_RANDOM_WAIT))  # Wait a random amount of seconds
    print("Sending request accepted message...")
    return send_message(comms_info.destination_pipe_address, REQUEST_ACC_MSG, nrf)

def anyTransmitAcc():
    """
    Waits for a transmit accepted message. (<- TransmitAccMsg)
    
    Parameters:
    - comms_info: Communication information object.
    
    Returns:
    - True if acknowledgment is received, False otherwise.
    """
    return wait_for_desired_message(comms_info, TRANSMIT_ACC_MSG, TIMEOUT, nrf)

def needToBackOff():
    """
    Checks if backoff is necessary before transmitting data.
    
    Returns:
    - True if backoff is needed, False otherwise.
    """
    nrf.listen = True  # put radio into RX mode and power up

    start = time.monotonic()
    for count in range(0):
        if nrf.available():
            print(nrf.read())
            print("Need To Back Off")
            time.sleep(0.1)  # Wait for a short time before checking again
        else:
            return False
    
    return False

def packageTransmission():
    #nrf.auto_ack = False
    wait_for_desired_message(comms_info, REQUEST_ACC_MSG, TIMEOUT, nrf)
    """
    Manages the transmission of a data package.
    Changes to Channel 2
    Enables ack
    Parameters:
    - comms_info: Communication information object.
    
    Returns:
    - True if the package is transmitted successfully, False otherwise.
    """
    path = FOLDER_PATH  # Ruta completa al archivo en el directorio /mnt/usbdrive
    filelist = np.array([os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]) # Get the list of files in the directory
    filelist = filelist[np.where([x.endswith(".txt") and not x.startswith(".") for x in filelist])[0]] # Get the elements that end with ".txt" and does not start with "."
    print("filelist",filelist)
    if not os.path.exists(path):
        print(f"Path not found: {path}")
        return True
    if len(filelist) == 0:
        print(f"No files in: {path}")
        return True
    
    data = transmitter(comms_info, filelist, TRANSMIT_ATTEMPTS, nrf)
    return data

def sendFileRequest():
    """
    Sends a file request message to the receiving device. (-> FileRequestMsg)
    
    Parameters:
    - comms_info: Communication information object.
    """
    print("Sending file request...")
    r = send_message(comms_info.destination_pipe_address, FILE_REQUEST_MSG, nrf)
    
    if r:
        print("Message Sent")
    else:
        print("Fail while sending message")
    return r

def anyCarrier():
    """
    Checks for the presence of a carrier signal in the communication channel.
    Waits for a request accepted message. (<- RequestAccMsg)

    Parameters:
    - comms_info: Communication information object.
    
    Returns:
    - True if a carrier signal is detected, False otherwise.
    """
    return wait_for_desired_message(comms_info, REQUEST_ACC_MSG, TIMEOUT, nrf) 

def sendTransmitionAccepted():
    """
    Sends a transmission acceptance message to the sending device. (-> TRANSMIT_ACC_MSG)
    
    Parameters:
    - comms_info: Communication information object.
    """
    print("Sending transmission accepted message...")
    r = send_message(comms_info.destination_pipe_address, TRANSMIT_ACC_MSG, nrf)
    
    if r:
        print("Message Sent")
    else:
        print("Fail while sending message")
    return r

def packageReception():
    """
    Manages the reception of a data package.
    Changes to Channel 2
    Enables ack
    
    Parameters:
    - comms_info: Communication information object.
    
    Returns:
    - True if the package is received successfully, False otherwise.
    """
    #nrf.auto_ack = False
    nrf.channel = CHANNEL2
    send_message(comms_info.destination_pipe_address, REQUEST_ACC_MSG, nrf)
    time.sleep(0.1)
    receiver(comms_info, TIMEOUT, nrf)
    return False
    #nrf.auto_ack = False

# State Machine
class StateMachine:
    def __init__(self):
        self.state = "Check File State"

    def run(self):
        stop = False
        while True and not stop:
            print(f"\n\n#--------- CURRENT STATE: {self.state} ---------#")
            print(f"Channel Information: {comms_info}")
            time.sleep(1)
            if self.state == "Check File State":
                self.check_file_state()
            elif self.state == "Packet Possession State":
                self.packet_possession_state()
            elif self.state == "Request Accepted State":
                self.request_accepted_state()
            elif self.state == "Packet Transmission State":
                self.packet_transmission_state()
                stop = True
            elif self.state == "Send Request State":
                self.send_request_state()
            elif self.state == "Transmit Confirmation State":
                self.transmit_confirmation_state()
            elif self.state == "Packet Reception State":
                self.packet_reception_state()
                stop = True

    def check_file_state(self):
        """
        Checks if a file exists and transitions accordingly.
        """
        wait_for_usb()
        if checkFileExists():
            ledOn()
            comms_info.listening_pipe_address = BROADCAST_ID
            comms_info.destination_pipe_address = BROADCAST_ID
            set_pipes(comms_info, nrf)
            self.state = "Packet Possession State"
        else:
            comms_info.listening_pipe_address = MY_PIPE_ID
            comms_info.destination_pipe_address = BROADCAST_ID
            set_pipes(comms_info, nrf)
            self.state = "Send Request State"

    def packet_possession_state(self):
        """
        Manages packet possession state and transitions accordingly.
        """
        if anySupplicant():
            comms_info.listening_pipe_address = MY_PIPE_ID
            # Se define la destination pipe en la función de any Supplicant
            set_pipes(comms_info, nrf)
            self.state = "Request Accepted State"
        else:
            self.state = "Packet Possession State"

    def request_accepted_state(self):
        """
        Manages request accepted state and transitions accordingly.
        """
        if not sendRequestAcc():
            comms_info.listening_pipe_address = BROADCAST_ID
            comms_info.destination_pipe_address = BROADCAST_ID
            set_pipes(comms_info, nrf)
            self.state = "Packet Possession State"
        else:
            if anyTransmitAcc():
                # Las pipes ya estan bien definidas
                comms_info.channel = CHANNEL2
                nrf.channel = CHANNEL2
                self.state = "Packet Transmission State"
            else:
                comms_info.listening_pipe_address = BROADCAST_ID
                comms_info.destination_pipe_address = BROADCAST_ID
                set_pipes(comms_info, nrf)
                self.state = "Packet Possession State"

    def packet_transmission_state(self):
        """
        Manages packet transmission state and transitions accordingly.
        """
        comms_info.channel = CHANNEL2
        nrf.channel = CHANNEL2
        if not needToBackOff():
            packageTransmittedFlag = packageTransmission()
            nrf.flush_rx()
            nrf.flush_tx()
            nrf.power = False
            nrf.power = True
            print("Packet Sent Correctly:", packageTransmittedFlag)
        
        comms_info.channel = CHANNEL1
        nrf.channel = CHANNEL1
        # TODO pensar en esto
        comms_info.listening_pipe_address = BROADCAST_ID
        comms_info.destination_pipe_address = BROADCAST_ID
        set_pipes(comms_info, nrf)
        print("CHANNEL IS : ", nrf.channel)
        nrf.open_tx_pipe(BROADCAST_ID)
        # set RX address of TX node into an RX pipe
        nrf.open_rx_pipe(1, BROADCAST_ID)
        self.state = "Packet Possession State"

    def send_request_state(self):
        """
        Manages send request state and transitions accordingly.
        """
        carrierFlag = False
        time.sleep(random.randint(0, FILE_REQUEST_RANDOM_WAIT))  # Wait a random amount of seconds
        if sendFileRequest():
            carrierFlag = anyCarrier()
        if carrierFlag:
            comms_info.listening_pipe_address = MY_PIPE_ID
            # Se define la destination pipe en la función de any Supplicant
            set_pipes(comms_info, nrf)
            self.state = "Transmit Confirmation State"
        else:
            comms_info.listening_pipe_address = MY_PIPE_ID
            comms_info.destination_pipe_address = BROADCAST_ID
            set_pipes(comms_info, nrf)
            self.state = "Send Request State"

    def transmit_confirmation_state(self):
        """
        Manages transmit confirmation state and transitions accordingly.
        """
        sendTransmitionAccepted()
        nrf.ack = True
        comms_info.channel = CHANNEL2
        self.state = "Packet Reception State"

    def packet_reception_state(self):
        """
        Manages packet reception state and transitions accordingly.
        """
        comms_info.channel = CHANNEL2
        nrf.channel = CHANNEL2
        packageReceivedFlag = packageReception()
        nrf.flush_rx()
        nrf.flush_tx()
        nrf.power = False
        nrf.power = True
        comms_info.channel = CHANNEL1
        nrf.channel = CHANNEL1
        if packageReceivedFlag:
            ledOn()
            comms_info.listening_pipe_address = BROADCAST_ID
            comms_info.destination_pipe_address = BROADCAST_ID
            set_pipes(comms_info, nrf)
            print(nrf.channel)
            self.state = "Packet Possession State"
        else:
            comms_info.listening_pipe_address = MY_PIPE_ID
            comms_info.destination_pipe_address = BROADCAST_ID
            set_pipes(comms_info, nrf)
            self.state = "Send Request State"
        nrf.open_tx_pipe(BROADCAST_ID)
        # set RX address of TX node into an RX pipe
        nrf.open_rx_pipe(1, BROADCAST_ID)
# Main
if __name__ == "__main__":
    sm = StateMachine()
    sm.run()
