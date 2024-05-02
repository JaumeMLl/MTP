from circuitpython_nrf24l01.rf24 import RF24

nrf = RF24()

def TX(num_packets, data):

    nrf.listen = False  # Put radio in TX mode (Used also for power saving)

    return 