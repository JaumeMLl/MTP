from RF24 import *
import RPi.GPIO as GPIO


def configure_radios(channel_TX, channel_RX, function):

    # Setup CE and CSN pin with SPI velocity and define pipe adresses depending if it acts as a transmitter or as a receiver
    if (function==1):
        radio_rx = RF24(RPI_V2_GPIO_P1_13, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)
        radio_tx = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS1, BCM2835_SPI_SPEED_8MHZ)
        pipes = [0xf0f0f0f0e1, 0xf0f0f0f0d2]
    else:
        radio_tx = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS1, BCM2835_SPI_SPEED_8MHZ)
        radio_rx = RF24(RPI_V2_GPIO_P1_13, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)
        pipes = [0xf0f0f0f0d2, 0xf0f0f0f0e1]
	
    # Initialize the transceivers
    radio_rx.begin()
    radio_tx.begin()

    # Set the Radio Channels
    radio_tx.setChannel(channel_TX)
    radio_rx.setChannel(channel_RX)

    # Set configuration power
    radio_tx.setPALevel(RF24_PA_LOW)
    radio_rx.setPALevel(RF24_PA_LOW)

    # Disable auto ACK
    radio_tx.setAutoAck(False)
    radio_rx.setAutoAck(False)
    radio_tx.enableDynamicPayloads()
    radio_rx.enableDynamicPayloads()

    # Open writing and reading pipe
    radio_tx.openWritingPipe(pipes[1])
    radio_tx.openReadingPipe(1,pipes[0])
    radio_rx.openWritingPipe(pipes[1])
    radio_rx.openReadingPipe(1, pipes[0])

    print("Transmitter configuration")
    radio_tx.printDetails()

    print("Receiver configuration")
    radio_rx.printDetails()

    return radio_tx, radio_rx
