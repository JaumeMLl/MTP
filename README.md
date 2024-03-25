# MTP - Equipo C

## Pins

### Raspberry Pins

![image](https://github.com/JaumeMLl/MTP/assets/79020335/56c1852d-722d-4a0a-a04f-dab25f8d7b9f)

Important: The CE in the raspberry corresponds to the chip select (In the transiver this pin is called CSE).

### Transceiver pins

![image](https://github.com/JaumeMLl/MTP/assets/79020335/69e355a9-380a-4f6b-b806-965cf8a60c7a)

Important: The CE in the transciver corresponds to chip enable

### Conexions

The result of the conections is the following:

![image](https://github.com/JaumeMLl/MTP/assets/79020335/0083fcaa-c694-42ba-a04e-3c7a673e12fe)


## Library imports

`pip install board` - library needen for CircuitPython_nRF24L01

`pip install Adafruit-Blinka` - library needed for CircuitPython_nRF24L01. Resolves No module named 'digitalio'
