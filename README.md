# MTP - Equipo C
<<<<<<< HEAD

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
=======
# Instrucciones para Crear la SSH Key para GitHub
>>>>>>> 0ee453c5ed5b5a67ecded36ce51ef372dba4969e

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
   Ve a GitHub y inicia sesión.
   Haz clic en tu foto de perfil en la esquina superior derecha y selecciona Settings.
   En el menú lateral, selecciona SSH and GPG keys.
   Haz clic en el botón New SSH key.
   En el campo "Title", añade un nombre descriptivo para tu llave. Por ejemplo, "Raspberry Pi key".
   En el campo "Key", pega la llave SSH pública que copiaste anteriormente.
   Haz clic en Add SSH key.
<<<<<<< HEAD
7. Finalmente, esto te confirmará si está bien creada la clave SSH:
   ```bash 
   ssh -T git@github.com
=======
 7. Finalmente, esto te confirmará si está bien creada la clave SSH:
   ```bash 
   ssh -T git@github.com
   ```


# Versiones

En la carpeta CircuitPython_nRF24L01 encontrarás los ejemplos originales para realizar los tests más simples.

En la carpeta QM están las tres versiones del Quick Mode (QM):

- V0: La versión más simple de todas. El emisor envia el fichero .txt del directorio fragmentado pero sin acks ni ningun tipo de comprobación. El receptor solo crea fichero .txt con la info en el mismo directorio de trabajo.
- V1: Se añaden acks. Modificar count con el numero de reintentos deseados
- V2: Se lee el fichero mtp.txt desde mnt/usbdrive donde se encuentra el usb, se envia su contenido (con acks para cada fragmento) y en el receptor se crea el .txt en el directorio de trabajo y en el directorio mnt/usbdrive donde se encuentra el usb del receptor

# Información Adicional

Para el directorio del usb con permisos de escritura (y de lectura) 

1. 
   ```bash 
   lsblk
   ```
2. 
   ```bash 
   sudo blkid
   ```
3.  
   ```bash 
   sudo mount -t vfat -o uid=pi,gid=pi /dev/sda1 /mnt/usbdrive
   ```


>>>>>>> 0ee453c5ed5b5a67ecded36ce51ef372dba4969e

# Canals de NRF2401
Referència: https://lastminuteengineers.com/nrf24l01-arduino-wireless-communication/#rf-channel-frequency
Hi ha una imatge on mostra el següent: 

- Canals del 1 al 125
- Espaiats cada 1MHz


Per escollir el canal hem de fer això: 
> Freq(Selected) = 2400 + CH(Selected)

*Nota important* --> Sobretot per al NM
> At 250kbps and 1Mbps air data rates, each channel takes up less than 1 MHz of bandwidth, so there is a 1 MHz gap between the two channels. However, for a 2 Mbps air data rate, 2MHz of bandwidth is required (greater than the resolution of the RF channel frequency setting). So, in 2 Mbps mode, keep a 2MHz gap between the two channels to ensure non-overlapping channels and reduce cross-talk.
