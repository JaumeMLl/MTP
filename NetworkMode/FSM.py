import random

# Constants
TIMEOUT = 10
CHANNEL1 = 1
CHANNEL2 = 2
BROADCAST_ID = "broadcast"

# Variables
class CommsInfo:
    def __init__(self):
        self.rxId = None
        self.myId = None
        self.channel = None

commsInfo = CommsInfo()
fileFlag = False

# Functions
def checkFileExists():
    # Function to check if file exists inside the computer
    pass

def anySupplicant(commsInfo):
    # Function to listen to channel 1 for File Request
    # and search in the buffer for File Request
    # returns True if there is any supplicant, sets the value of rxId
    pass

def sendClaimMessage(commsInfo):
    # Function to send Claim Message to the supplicant with id rxId inside commsInfo object.
    pass

def anyTransmitConfirmation(rxInfo):
    # Function to listen to channel 1 for Transmit Confirmation ACK
    # Search in the buffer for Transmit Confirmation ACK with its own destination id
    # Flush other messages. There must be a timeout inside this function
    pass

def packageTransmition(commsInfo):
    # Function to transmit a package
    pass

def sendFileRequest(destination):
    # Function to send a file request
    pass

def anyCarrier(commsInfo):
    # Function to listen through channel 1 searching for any carrier response
    pass

def flushBuffer():
    # Function to flush the buffer
    pass

def packageReception(commsInfo):
    # Function to receive a package
    pass

# States
class StateMachine:
    def __init__(self):
        self.state = self.check_state

    def check_state(self):
        fileFlag = checkFileExists()
        if fileFlag:
            self.state = self.packet_possession_state
        else:
            self.state = self.file_request_state

    def packet_possession_state(self):
        supplicantFlag = anySupplicant(commsInfo)
        if supplicantFlag:
            self.state = self.claim_message_state

    def claim_message_state(self):
        sendClaimMessage(commsInfo)
        transmitConfirmationFlag = anyTransmitConfirmation(commsInfo)
        if transmitConfirmationFlag:
            self.state = self.carrier_packet_transition_state
        else:
            self.state = self.packet_possession_state

    def carrier_packet_transition_state(self):
        commsInfo.channel = CHANNEL2
        packageTransmittedFlag = packageTransmition(commsInfo)
        print("Packet Sent Correctly:", packageTransmittedFlag)
        self.state = self.packet_possession_state

    def send_request_state(self):
        sendFileRequest(BROADCAST_ID)
        carrierFlag = anyCarrier(commsInfo)
        if carrierFlag:
            self.state = self.transmit_confirmation_state
        else:
            self.state = self.send_request_state

    def transmit_confirmation_state(self):
        flushBuffer()
        sendFileRequest(commsInfo)
        self.state = self.packet_transmission_state

    def packet_transmission_state(self):
        commsInfo.channel = CHANNEL2
        packageReceivedFlag = packageReception(commsInfo)
        if packageReceivedFlag:
            self.state = self.packet_possession_state
        else:
            self.state = self.send_request_state

    def run(self):
        while True:
            if self.state == self.check_state:
                self.check_state()
            elif self.state == self.packet_possession_state:
                self.packet_possession_state()
            elif self.state == self.claim_message_state:
                self.claim_message_state()
            elif self.state == self.carrier_packet_transition_state:
                self.carrier_packet_transition_state()
            elif self.state == self.send_request_state:
                self.send_request_state()
            elif self.state == self.transmit_confirmation_state:
                self.transmit_confirmation_state()
            elif self.state == self.packet_transmission_state:
                self.packet_transmission_state()

if __name__ == "__main__":
    sm = StateMachine()
    sm.run()
