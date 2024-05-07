## SFM:

```
# constants
constant TIMEOUT;
constant CHANNEL1;
constant CHANNEL2;
constant BROADCAST_ID;
cosntant myID;

constant fileRequest = xxx
constant requestAcc = xxx

# Variables
CommsInfo commsInfo {
	int rxId
	int myId
	int channel
}

bool fileFlag;
```

## Check State
```
- Check File State: 
	+ During:
		self.fileFlag = checkFileExists() # Check if file exists file inside computer
	+ Transition: if(fileFlag == True) #Do I have the file?
		True
			insertFileCode(); #make code accecible in the code
			ledOn(); #lights a led
			state = Packet Possession State
		False
			state = File Request State
```

## Carrier
```
- Packet Possession State:
	+ During:
		supplicantFlag = anySupplicant() # Listens channel 1 for File Request, search in the buffer for File Request, flush other messages. returns true if there is any suppliocant, sets the value of rxId
	+ Transition1: if(supplicantFlag == True) # Any Send Request from supplicant?
		True
			state = Request Accepted State
		False
			state = Packet Possession State.
		
- Request Accepted State:
	+ During:
		sendRequestAcc(commsInfo) # Send Request Accepted Message to the supplicant with id rxId. Add header with myId
		transmitConfirmationFlag = anyTransmitAcc(rxInfo) # Listens channel 1 for Transmit Confirmation ACK. Search in the buffer for Transmit Confirmation ACK with its own destination id, flush other messages. There must be a timeOut inside this function
	+ Transition: if(transmitAccFlag == True)
		True
			state = Packet Transmission State.
		False
			state = Packet Possession State
	
- Packet Transition State:
	+ During:
		while(True = neddToBackOff() || exit == true){ # listens to the channel and waits to be available to transmit
			#do nothing
			if(i < TIMEOUT){
				exit = true
			}
			i++;
		}
		if(exit != true){
			packageTransmittedFlag = packageTransmition(commsInfo) # Must change the channel and start a 1 to 1 communication
			print("Packet Sent Correcly:" + packageTransmittedFlag)
		}
		#reset internal variables
		exit = false
		i = 0;
	+ Transition:
		state = Packet Possession State
```

## Supplicant

```
- Send Request State:

	+ During:
		sendFileRequest(BROADCAST_ID) # Through channel 1, send request to all neighbors (broadcast)
		carrierFlag = anyCarrier(commsInfo) #Liten through channel 1 searching any Reuqest Accepted
		wait(x) # Wait a random amount of seconds to transmit again. Make it a long time to avoid interferences (5 seconds)
	+ Transition: if(carrierFlag = True) # Do I have any response? 
		True
			state = Transmit Confirmation State.
		False
			state = Send Request State.

- Transmit Confirmation State: 
	+ During:
		sendTransmitionAccepted(commsInfo) # Through channel 1, Send a Transmit Confirmation ACK to the carrier
	+ Transition:
		state = Packet Reception State
		
- Packet Reception State:
	+ During:
		packageReceivedFlag = packageReception(commsInfo)
	+ Transition: packageReceivedFlag == True # Transmission Acomplished?
		True
			ledOn();
			state = Packet Possession State
		False
			state = Send Request State
```