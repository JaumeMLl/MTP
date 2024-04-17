from asyncio import sleep
import random
import time

# Constants
TIMEOUT = 10
CHANNEL1 = 1
CHANNEL2 = 2
BROADCAST_ID = "broadcast"
MY_ID = "myID"

# Variables
class CommsInfo:
    def __init__(self, rxId=None, myId=MY_ID, channel=None):
        self.rxId = rxId
        self.myId = myId
        self.channel = channel

commsInfo = CommsInfo()
fileFlag = False

# Functions
def checkFileExists():
    # Implementation to check if file exists
    r = False # For testing purposes
    if r:
        print("File Found")
    else:
        print("File NOT Found")
    return r
def ledOn():
    # Implementation to turn on LED
    print("Turning LED on...")

def anySupplicant(commsInfo):
    # Implementation to check for any supplicant
    r = True # For testing purposes
    if r:
        print("Send Request Received")
    else:
        print("Send Request NOT Received")
    return r

def sendRequestAcc(commsInfo):
    # Implementation to send request accepted message
    print("Sending request accepted message...")

def anyTransmitAcc(commsInfo):
    # Implementation to check for transmit confirmation ACK
    r = True # For testing purposes
    if r:
        print("Transmit Accepted Received")
    else:
        print("Transmit Accepted NOT Received")
    return r  

def needToBackOff():
    # Implementation to check if backoff is needed
    r = False # For testing purposes
    if r:
        print("Need To Back Off")
    else:
        print("NO Need To Back Off")
    return r

def packageTransmission(commsInfo):
    # Implementation for package transmission
    r = True # For testing purposes
    if r:
        print("Package Transmission Accomplished")
    else:
        print("Package Transmission Failed")
    return r 

def sendFileRequest(commsInfo):
    # Implementation to send file request
    print("Sending file request...")

def anyCarrier(commsInfo):
    # Implementation to check for any carrier
    r = True # For testing purposes
    if r:
        print("Request Accepted Received")
    else:
        print("Carrier NOT Found")
    return r  

def sendTransmitionAccepted(commsInfo):
    # Implementation to send transmission accepted message
    print("Sending transmission accepted message...")

def packageReception(commsInfo):
    # Implementation for package reception
    r = True # For testing purposes
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
        
        if checkFileExists():
            ledOn()
            self.state = "Packet Possession State"
        else:
            self.state = "Send Request State"

    def packet_possession_state(self):
        supplicantFlag = anySupplicant(commsInfo)
        if supplicantFlag:
            self.state = "Request Accepted State"
        else:
            self.state = "Packet Possession State"

    def request_accepted_state(self):
        sendRequestAcc(commsInfo)
        transmitAccFlag = anyTransmitAcc(commsInfo)
        if transmitAccFlag:
            self.state = "Packet Transmission State"
        else:
            self.state = "Packet Possession State"

    def packet_transmission_state(self):
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
        sendFileRequest(commsInfo)
        carrierFlag = anyCarrier(commsInfo)
        if carrierFlag:
            self.state = "Transmit Confirmation State"
        else:
            time.sleep(random.randint(1, 5))  # Wait a random amount of seconds
            self.state = "Send Request State"

    def transmit_confirmation_state(self):
        sendTransmitionAccepted(commsInfo)
        self.state = "Packet Reception State"

    def packet_reception_state(self):
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
