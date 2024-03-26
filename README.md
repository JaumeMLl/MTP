# MTP - Equipo C
# Instrucciones para Crear la SSH Key para GitHub

Para crear la clave SSH de GitHub, sigue estos pasos en la terminal:

1. Genera una nueva clave SSH utilizando tu correo electrónico como etiqueta:
   ```bash
   ssh-keygen -t rsa -b 4096 -C "tu_email@example.com"
2. Inicia el agente SSH en segundo plano:
   eval "$(ssh-agent -s)"
3. Añade tu clave SSH al ssh-agent:
   ssh-add ~/.ssh/id_rsa
