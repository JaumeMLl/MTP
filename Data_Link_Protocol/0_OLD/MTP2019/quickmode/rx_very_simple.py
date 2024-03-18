from __future__ import print_function
import time
from RF24 import *
import zlib
from utils.radio import configure_radios
from utils.config import get_args, process_config
from utils.packet_manager_simple import PacketManagerAck
from utils.ledManager import ledManager

"""
TODO: Create packet manager that reassembles the packets instead of reassembling the packets in the last if
"""


try:
    args = get_args()
    config = process_config(args.config)

except:
    print("missing or invalid arguments")
    exit(0)

millis = lambda: int(round(time.time() * 1000))

print('Quick Mode script! ')

print('RX Role:Pong Back, awaiting transmission')

# Set led Manager
led = ledManager()
led.red()

# Set comunication parameters
channel_RX = 60
channel_TX = 70

# Initialize radio
radio_tx, radio_rx = configure_radios(channel_TX, channel_RX,0)
radio_rx.startListening()
radio_tx.stopListening()

# Create local variables
frames = []
last_packet = False
num_packets = 0
num_file = 0

# Create Ack packet
packet_manager_ack = PacketManagerAck()
packet_ack = packet_manager_ack.create()

led.blue()
loop = 1
packet_number = 0

# forever loop
while loop:

    # Pong back role.  Receive each packet, dump it out, and send ACK
    if radio_rx.available():
        while radio_rx.available():
            #First check of the payload
            len = radio_rx.getDynamicPayloadSize()
            receive_payload = radio_rx.read(radio_rx.getDynamicPayloadSize())
            #print('Got payload eot={} value="{}"'.format(receive_payload[0], receive_payload[1:31].decode('utf-8')))
            
            # Save it if is not a duplicate packet
            print('received_payload'+str(receive_payload[0]))
            if receive_payload[0] == packet_number:
                packet_number = (packet_number+1)%2
                print('packet number'+str(packet_number))
                # Append the information
                frames += receive_payload[2:]
            
            # Check if it is last packet            
            if receive_payload[1] == 1:
                print('Last packet')
                last_packet = True

            # Send Ack
            radio_tx.write(bytes([0]))
            print('Sent response.')

            # If it is the last packet save the txt
            if last_packet:
                #led.green()
                print('Reception complete.')
                # If we are here it means we received all the frames so we have to uncompress
                print("Type of the list")
                print(type(frames))
                print("Type of one element")
                print(type(frames[0]))
                uncompressed_frames = zlib.decompress(bytes(frames))
                f = open('file'+str(num_file)+'.txt','wb')
                f.write(bytes(uncompressed_frames))
                f.close()
                print('File saved')
                frames = []
                last_packet = False
                num_packets = 0
                num_file += 1
                input('Press Enter to finish')
                led.off()
                loop = 0
