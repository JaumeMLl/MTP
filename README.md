MTP - Equipo C
Instrucciones para Crear la SSH Key para GitHub
Para crear la clave SSH de GitHub, sigue estos pasos en la terminal:

Genera una nueva clave SSH utilizando tu correo electrónico como etiqueta:
ssh-keygen -t rsa -b 4096 -C "tu_email@example.com"
Inicia el agente SSH en segundo plano:
eval "$(ssh-agent -s)"
Añade tu clave SSH al ssh-agent:
ssh-add ~/.ssh/id_rsa
Copia exactamente lo que salga al ejecutar:
cat ~/.ssh/id_rsa.pub
Luego, sigue estos pasos en GitHub: Ve a GitHub y inicia sesión. Haz clic en tu foto de perfil en la esquina superior derecha y selecciona Settings. En el menú lateral, selecciona SSH and GPG keys. Haz clic en el botón New SSH key. En el campo "Title", añade un nombre descriptivo para tu llave. Por ejemplo, "Raspberry Pi key". En el campo "Key", pega la llave SSH pública que copiaste anteriormente. Haz clic en Add SSH key.
Finalmente, esto te confirmará si está bien creada la clave SSH:
ssh -T git@github.com
Información Adicional
En la carpeta CircuitPython_nRF24L01 encontrarás los ejemplos originales para realizar los tests más simples.

En la carpeta QM están las tres versiones del Quick Mode (QM):

V0: La versión más simple de todas. El emisor, cuando se le pide por terminal que ponga la T de emisor, lo ha de seguir con el string que quiere transmitir. Por ejemplo: T HOLA MUNDO. En esta versión, el receptor solo escucha y no hay ningún tipo de comprobación.
V1: En esta versión se añade un checksum y se fragmenta el array a transmitir. Como 1 byte es de checksum, los chunks creados al fragmentar siempre son iguales o menores que 30 bytes. El receptor envía ACK si el checksum es correcto.
VFinal: Esta versión, en caso de funcionar, ya serviría para el QM. Primero lee el fichero mtp.txt que se encuentra en el mismo directorio, lo fragmenta en chunks y luego comprime cada uno de ellos. Ninguno de estos chunks puede pasar de los 30 bytes, igual que en V1, y aquí el receiver, hasta que no ha recibido el paquete, descomprimido y comprobado que el checksum es correcto y que se puede descomprimir correctamente, no envía el ACK.
