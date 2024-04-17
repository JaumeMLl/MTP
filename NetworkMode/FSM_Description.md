## SFM:

```
# constants
constant TIMEOUT;
constant CHANNEL1;
constant CHANNEL2;
constant BROADCAST_ID;

# Variables
CommsInfo commsInfo;
	int rxId
	int myId
	int channel
bool fileFlag;
```

## Check State
```
- Check State: 
	+ Entry:
		self.fileFlag = checkFileExists() # Check if file exists file inside computer
	+ During:
		Do nothing
	+ Transition: fileFlag == True #Do I have the file?
		True -> Packet Possession State.
		False -> File Request State
```

## Carrier
```
- Packet Possession State:
	+ During:
		supplicantFlag = anySupplicant(commsInfo) # Listens channel 1 for File Request, search in the buffer for File Request, flush other messages. returns true if there is any suppliocant, sets the value of rxId
	+ Transition1: supplicantFlag == True # Any Send Request from supplicant?
		No -> Packet Possession State.
		Yes -> Claim Message State
		
- Claim Message State:
	+Entry:
		sendClaimMessage(commsInfo) # Send Claim Message to the supplicant with id rxId inside commsInfo object.
	+ During:
		transmitConfirmationFlag = anyTransmitConfirmation(rxInfo) # Listens channel 1 for Transmit Confirmation ACK. Search in the buffer for Transmit Confirmation ACK with its own destination id, flush other messages. There must be a timeOut inside this function)
	+ Transition1: transmitConfirmationFlag == True?
		Yes -> Carrier Packet Transition State.
		No -> Packet Possession State
	
- Carrier Packet Transition State:
	+ Entry:
		commsInfo.setChannel(CHANNEL2)
	+ During:
		packageTransmittedFlag = packageTransmition(commsInfo)
		print("Packet Sent Correcly:" + packageTransmittedFlag)
	+ Transition:
		-> Packet Possession State
```

## Supplicant

```
- Send Request State:

	+ During:
		sendFileRequest(BROADCAST_ID) # Through channel 1, send request to all neighbors (broadcast)
		carrierFlag = anyCarrier(commsInfo) #Liten through channel 1 searching for any carrier response
		wait(x) # Wait a random amount of seconds to transmit again
	+ Transition: carrierFlag = True # Do I have any response? 
		Yes -> Transmit Confirmation State.
		No -> Send Request Statee.

- Transmit Confirmation State: 
	+ Entry:
		flushBuffer() # Flush Buffer
	+ During:
		sendFileRequest(commsInfo) # Through channel 1, Send a Transmit Confirmation ACK to the carrier
	+ Transition:
		-> Packet Transmision State
- Packet Transmision State:
	+ Entry:
		commsInfo.setChannel(CHANNEL2)
	+ During:
		packageReceivedFlag = packageReception(commsInfo)
	+ Transition: packageReceivedFlag == True # Transmission Acomplished?
		Yes -> Packet Possession State
		No -> Send Request State
```