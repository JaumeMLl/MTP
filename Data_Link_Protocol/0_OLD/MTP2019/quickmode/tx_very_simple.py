from __future__ import print_function
import time
from RF24 import *

from utils.packet_manager_simple import PacketManager
from utils.radio import configure_radios
from utils.config import get_args, process_config
from utils.ledManager import ledManager

try:
    args = get_args()
    config = process_config(args.config)

except:
    print("missing or invalid arguments")
    exit(0)

millis = lambda: int(round(time.time() * 1000))

print('Quick Mode script! ')

print('TX Role: Ping Out, starting transmission')

# Set led Manager
led = ledManager()
led.red()

# Define comunication parameters
channel_TX = 60
channel_RX = 70
payload_size = config.payload_size

# Start radios
radio_tx, radio_rx = configure_radios(channel_TX, channel_RX,1)
radio_rx.startListening()
radio_tx.stopListening()

# Create packets
packet_manager = PacketManager(config.document_path)
packets = packet_manager.create()

#Define loop variables

# loop over the packets to be sent
led.violet()
i=0
tot_packets = len(packets)
for packet in packets:
    #Send the packet
    radio_tx.write(packet)
    print('Sending packet ' + str(i) + '/' + str(tot_packets))
    i+=1

    # Reset variables

    timeout = False
    retransmit = False
    num_retransmissions = 0
    ack_received = False

    while not ack_received:
	    # Start timing
        started_waiting_at = millis()
        while (not radio_rx.available()) and (not timeout):
            if (millis() - started_waiting_at) > int(config.timeout_time):
                timeout = True
        # In case of time out: Resend
        if timeout:
            led.yellow()
            print('failed, response timed out.')
            num_retransmissions += 1
            print("Timeout --> resending message")
            print("Retransmission number {}".format(num_retransmissions))
            radio_tx.write(packet)
            timeout = False
        else:
            led.violet()
            # Grab the response
            ack = radio_rx.read(1)
            print('got response:{}'.format(ack))
            #  Analyze ACK
            if ack == bytes([0]):
                print("ACK Received --> transmit the next packet")
                ack_received = True

led.off()
