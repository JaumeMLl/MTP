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

### Configure USB
To automatically mount any USB drive connected in the raspberry do:

Install:
 
  `sudo apt install usbmount`

Then do:
1. Edit the following file in an editor:

`sudo nano /lib/systemd/system/systemd-udevd.service`

2. Look for the line with the contents: `PrivateMounts=yes`
3. Change the yes in the line to no, like so: `PrivateMounts=no`
4. reboot

Your USB devices should now auto mount at `/media/usb0`, `/media/usb1` and so on.

De hecho, como nuestra raspberry solo tiene un puerto USB, estará siempre en `/media/usb/`

Reference: https://stackoverflow.com/questions/74474113/auto-mount-usb-drive-to-raspberry-pi-without-boot

### Configure USB ethernet
In windows, all the files need to be edited with `Notepad++` if not, you could destroy the format.
1. Connect SD to PC.
2. Edit the file `config.txt` in the `bootfs` partition. Append a new line: `dtoverlay=dwc2` at the bottom of the file.
3. In the same file, comment the line that contains: `otg_mode=1` using #.
4. Save and close the file.
5. Edit the file `cmdline.txt` in the `bootfs` partition. Add `modules-load=dwc2,g_ether` after the `rootwait` command separated using spaces.
6. Save and close the file.
7. Add an empty file called: `ssh` in the `bootfs` partition.
8. Connect the raspberry to your computer using a good cable (important), through the data port (the middle one).
9. A new USB-Ethernet connection should appear. Select: Allow other network users to connect through this computer's Internet connection.

Reference: https://www.makeuseof.com/how-to-connect-raspberry-pi-to-laptop-or-pc-usb/
