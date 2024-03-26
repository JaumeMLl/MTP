# MTP - Equipo C
## LEDS
- LED BLAU INDICA USB BEN MUNTAT.
- LED GROC INDICA NETWORK MODE.
- 1R LED VERMELL INDICA RECEIVER.
- 2N LED VERMELL INDICA TRANSMITTER.
## FUNCIONS LEDS
- DURANT LA TRANSMISIONDEL SIMPLE MODE, ESPEREM LED VERD CENTRAL ACTIU (QUALSEVOL ALTRA COSA SERÀ CONSIDERADA ERROR).
- AL FINAL DE LA TRANSMISSIÓ EN EL TRANSMITTER: LED VERD Y GROC PARPADEJANT INDICA MISSATGE TRANSMES.
- AL FINAL DE LA TRANISMISSIÓ EN EL RECEPTOR: LED VERD Y GROC PARPADEJANT INDICA MISSATGE DESCOMPRIMIT CORRECTAMENT. POSERIORMENT, LED BLAU PARPADEJANT INDICA COPIA CORRECTA AL USB.
- AL FINAL DE LA TRANISMISSIÓ EN EL RECEPTOR: LEDS VERMELLS PARPADEJANT INDICA ERROR EN LA DESCOMPRESIÓ.

## Switch
![image](https://github.com/JaumeMLl/MTP/assets/72398466/7b1dae60-33d9-4ad9-a16c-c2d5f9ae2a64)
- Sw1 = RX/TX: UP is RX, DOWN is TX
- SW2 = NW: UP is NW off, DOWN is NW on
- SW3 = ---

## Pins

### Raspberry Pins

![image](https://github.com/JaumeMLl/MTP/assets/79020335/56c1852d-722d-4a0a-a04f-dab25f8d7b9f)

Important: The CE in the raspberry corresponds to the chip select (In the transiver this pin is called CSE).

### Transceiver pins

![image](https://github.com/JaumeMLl/MTP/assets/79020335/69e355a9-380a-4f6b-b806-965cf8a60c7a)

Important: The CE in the transciver corresponds to chip enable

### Fer que s'executi el .py directament al obrir la raspy

1. Crear un file systemd --> **my_script** es pot canviar 

`sudo nano /etc/systemd/system/Single_Mode.service`

2. Afegir el següent contingut --> S'ha d'editar la ubicació corresponent de l'script

```
[Unit]
Description=My Python Script
After=multi-user.target

[Service]
User=pi
ExecStart=/usr/bin/python3 /home/pi/SM/Single_Mode.py 

[Install]
WantedBy=multi-user.target
```
3. Guardar i sortir

4.
  `sudo systemctl daemon-reload`

5. Permetre aquest servei

`sudo systemctl enable Single_Mode.service`

5. Començar el servei

`sudo systemctl start Single_Mode.service`

!! Si no funciona fer un reboot !! (`sudo reboot`)

### Per desautomatitzar-ho: 

1. Obrim un terminal a la raspy

2. Desactivem el servei 

`sudo systemctl disable Single_Mode.service`

3. Parar el servei 

`sudo systemctl stop Single_Mode.service`

4. Reboot

`sudo reboot`


### Conexions

The result of the conections is the following:

![image](https://github.com/JaumeMLl/MTP/assets/79020335/0083fcaa-c694-42ba-a04e-3c7a673e12fe)

## SPI configuration Using "Raspi-config" on Command Line
From the command line or Terminal window start by running the following command :

`sudo raspi-config` - This will launch the raspi-config utility.

1. Select "Interfacing Options".
2. Highlight the "SPI" option and activate "-Select-".
3. Select and activate "-Yes-".
4. Highlight and activate "-Ok-".
5. When prompted to reboot highlight and activate "-Yes-".

The Raspberry Pi will reboot and the interface will be enabled.

## Library imports

`pip install board` - library needen for CircuitPython_nRF24L01

`pip install Adafruit-Blinka` - library needed for CircuitPython_nRF24L01. Resolves No module named 'digitalio'

## USB
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
5. Configurar permisos de usbmount.  El archivo de configuración se encuentra en /etc/usbmount/usbmount.conf.
6. Abre el archivo usbmount.conf como 'sudo nano' y busca la línea que comienza con MOUNTOPTIONS
7. Cambia la linea por: MOUNTOPTIONS="sync,noexec,nodev,noatime,nodiratime,uid=pi,gid=pi,dmask=000,fmask=111"
8. Guarda cambios y reinicia usbmount: sudo systemctl restart udisks2

Your USB devices should now auto mount at `/media/usb0`, `/media/usb1` and so on.

De hecho, como nuestra raspberry solo tiene un puerto USB, estará siempre en `/media/usb/`

Reference: https://stackoverflow.com/questions/74474113/auto-mount-usb-drive-to-raspberry-pi-without-boot
També recordar tema metadatos: fer ls -a al directory per veure TOTS els fitxers que hi ha.

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

En caso de que no te funcione podria ser fallo de los drivers.
Intenta con este video que complementa el tutorial anterior: https://www.youtube.com/watch?v=XaTmG708Mss

## Instrucciones para Crear la SSH Key para GitHub

Para crear la clave SSH de GitHub, sigue estos pasos en la terminal:

1. Genera una nueva clave SSH utilizando tu correo electrónico como etiqueta:
   ```bash
   ssh-keygen -t rsa -b 4096 -C "tu_email@example.com"
2. Inicia el agente SSH en segundo plano:
   ```bash
   eval "$(ssh-agent -s)"
4. Añade tu clave SSH al ssh-agent:
   ```bash
   ssh-add ~/.ssh/id_rsa
5. Copia exactamente lo que salga al ejecutar:
   ```bash
   cat ~/.ssh/id_rsa.pub
6. Luego, sigue estos pasos en GitHub:
6. Luego, sigue estos pasos en GitHub:
   Ve a GitHub y inicia sesión.
   Haz clic en tu foto de perfil en la esquina superior derecha y selecciona Settings.
   En el menú lateral, selecciona SSH and GPG keys.
   Haz clic en el botón New SSH key.
   En el campo "Title", añade un nombre descriptivo para tu llave. Por ejemplo, "Raspberry Pi key".
   En el campo "Key", pega la llave SSH pública que copiaste anteriormente.
   Haz clic en Add SSH key.
 7. Finalmente, esto te confirmará si está bien creada la clave SSH:
   ```bash 
   ssh -T git@github.com
   ```


Información Adicional
En la carpeta CircuitPython_nRF24L01 encontrarás los ejemplos originales para realizar los tests más simples.

En la carpeta QM están las tres versiones del Quick Mode (QM):

V0: La versión más simple de todas. El emisor, cuando se le pide por terminal que ponga la T de emisor, lo ha de seguir con el string que quiere transmitir. Por ejemplo: T HOLA MUNDO. En esta versión, el receptor solo escucha y no hay ningún tipo de comprobación.
V1: En esta versión se añade un checksum y se fragmenta el array a transmitir. Como 1 byte es de checksum, los chunks creados al fragmentar siempre son iguales o menores que 30 bytes. El receptor envía ACK si el checksum es correcto.
VFinal: Esta versión, en caso de funcionar, ya serviría para el QM. Primero lee el fichero mtp.txt que se encuentra en el mismo directorio, lo fragmenta en chunks y luego comprime cada uno de ellos. Ninguno de estos chunks puede pasar de los 30 bytes, igual que en V1, y aquí el receiver, hasta que no ha recibido el paquete, descomprimido y comprobado que el checksum es correcto y que se puede descomprimir correctamente, no envía el ACK.
