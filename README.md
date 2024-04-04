# MTP - Equipo C
# Instrucciones para Crear la SSH Key para GitHub

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


