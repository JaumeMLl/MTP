from asyncio import sleep
import random
import time
import os

# Constants
TIMEOUT = 10
CHANNEL1 = 1
CHANNEL2 = 2
BROADCAST_ID = "broadcast"
MY_ID = "myID"

# Variables
class CommsInfo:
    def __init__(self, rxId=None, myId=MY_ID, channel=None):
        """
        Initializes communication information.
        
        Parameters:
        - rxId: The ID of the receiving device.
        - myId: The ID of this device.
        - channel: The communication channel.
        """
        self.rxId = rxId
        self.myId = myId
        self.channel = channel

commsInfo = CommsInfo()
fileFlag = False

# Functions

def checkFileExists():
    """
    Checks if a file exists in the specified directory.
    
    Returns:
    - True if the file exists, False otherwise.
    """
    path = '/media/usb'  # Full path to the directory where the USB is mounted
    filelist = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
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
    print("Turning LED on...")

def anySupplicant(commsInfo):
    """
    Checks for any supplicant device in the communication channel.
    
    Parameters:
    - commsInfo: Communication information object.
    
    Returns:
    - True if a supplicant device is detected, False otherwise.
    """
    r = True  # For testing purposes
    if r:
        print("Send Request Received")
    else:
        print("Send Request NOT Received")
    return r

def sendRequestAcc(commsInfo):
    """
    Sends a request acceptance message to a requesting device.
    
    Parameters:
    - commsInfo: Communication information object.
    """
    print("Sending request accepted message...")

def anyTransmitAcc(commsInfo):
    """
    Checks for acknowledgment of transmission from the receiving device.
    
    Parameters:
    - commsInfo: Communication information object.
    
    Returns:
    - True if acknowledgment is received, False otherwise.
    """
    r = True  # For testing purposes
    if r:
        print("Transmit Accepted Received")
    else:
        print("Transmit Accepted NOT Received")
    return r  

def needToBackOff():
    """
    Checks if backoff is necessary before transmitting data.
    
    Returns:
    - True if backoff is needed, False otherwise.
    """
    r = False  # For testing purposes
    if r:
        print("Need To Back Off")
    else:
        print("NO Need To Back Off")
    return r

def packageTransmission(commsInfo):
    """
    Manages the transmission of a data package.
    
    Parameters:
    - commsInfo: Communication information object.
    
    Returns:
    - True if the package is transmitted successfully, False otherwise.
    """
    r = True  # For testing purposes
    if r:
        print("Package Transmission Accomplished")
    else:
        print("Package Transmission Failed")
    return r 

def sendFileRequest(commsInfo):
    """
    Sends a file request to the receiving device.
    
    Parameters:
    - commsInfo: Communication information object.
    """
    print("Sending file request...")

def anyCarrier(commsInfo):
    """
    Checks for the presence of a carrier signal in the communication channel.
    
    Parameters:
    - commsInfo: Communication information object.
    
    Returns:
    - True if a carrier signal is detected, False otherwise.
    """
    r = True  # For testing purposes
    if r:
        print("Request Accepted Received")
    else:
        print("Carrier NOT Found")
    return r  

def sendTransmitionAccepted(commsInfo):
    """
    Sends a transmission acceptance message to the sending device.
    
    Parameters:
    - commsInfo: Communication information object.
    """
    print("Sending transmission accepted message...")

def packageReception(commsInfo):
    """
    Manages the reception of a data package.
    
    Parameters:
    - commsInfo: Communication information object.
    
    Returns:
    - True if the package is received successfully, False otherwise.
    """
    r = True  # For testing purposes
    if r:
        print("Package Reception Accomplished")
    else:
        print("Package Reception Failed")
    return r

# State Machine
class StateMachine:
    def __init__(self):
        self.state = "Check File State"

    def run(self):
        while True:
            print("Current State:", self.state)
            time.sleep(1)
            if self.state == "Check File State":
                self.check_file_state()
            elif self.state == "Packet Possession State":
                self.packet_possession_state()
            elif self.state == "Request Accepted State":
                self.request_accepted_state()
            elif self.state == "Packet Transmission State":
                self.packet_transmission_state()
            elif self.state == "Send Request State":
                self.send_request_state()
            elif self.state == "Transmit Confirmation State":
                self.transmit_confirmation_state()
            elif self.state == "Packet Reception State":
                self.packet_reception_state()

    def check_file_state(self):
        """
        Checks if a file exists and transitions accordingly.
        """
        if checkFileExists():
            ledOn()
            self.state = "Packet Possession State"
        else:
            self.state = "Send Request State"

    def packet_possession_state(self):
        """
        Manages packet possession state and transitions accordingly.
        """
        supplicantFlag = anySupplicant(commsInfo)
        if supplicantFlag:
            self.state = "Request Accepted State"
        else:
            self.state = "Packet Possession State"

    def request_accepted_state(self):
        """
        Manages request accepted state and transitions accordingly.
        """
        sendRequestAcc(commsInfo)
        transmitAccFlag = anyTransmitAcc(commsInfo)
        if transmitAccFlag:
            self.state = "Packet Transmission State"
        else:
            self.state = "Packet Possession State"

    def packet_transmission_state(self):
        """
        Manages packet transmission state and transitions accordingly.
        """
        exit = False
        i = 0
        while needToBackOff() or exit:
            # do nothing
            if i >= TIMEOUT:
                exit = True
            i += 1
        if not exit:
            commsInfo.channel = CHANNEL2
            packageTransmittedFlag = packageTransmission(commsInfo)
            print("Packet Sent Correctly:", packageTransmittedFlag)
            commsInfo.channel = CHANNEL1
        self.state = "Packet Possession State"

    def send_request_state(self):
        """
        Manages send request state and transitions accordingly.
        """
        sendFileRequest(commsInfo)
        carrierFlag = anyCarrier(commsInfo)
        if carrierFlag:
            self.state = "Transmit Confirmation State"
        else:
            time.sleep(random.randint(1, 5))  # Wait a random amount of seconds
            self.state = "Send Request State"

    def transmit_confirmation_state(self):
        """
        Manages transmit confirmation state and transitions accordingly.
        """
        sendTransmitionAccepted(commsInfo)
        self.state = "Packet Reception State"

    def packet_reception_state(self):
        """
        Manages packet reception state and transitions accordingly.
        """
        commsInfo.channel = CHANNEL2
        packageReceivedFlag = packageReception(commsInfo)
        commsInfo.channel = CHANNEL1
        if packageReceivedFlag:
            ledOn()
            self.state = "Packet Possession State"
        else:
            self.state = "Send Request State"

# Main
if __name__ == "__main__":
    sm = StateMachine()
    sm.run()
