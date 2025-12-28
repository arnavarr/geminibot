#!/bin/bash

# Script de inicio de día: Sincronización y Procesamiento

# 1. Sincronizar correo
# Asumimos que mbsync está configurado. Descomentar si es necesario.
# echo "Sincronizando correos..."
# 
# 1.1 Refrescar Token OAuth2 (Microsoft)
# Asume que el archivo de token se llama 'microsoft_token.gpg'
TOKEN_FILE="microsoft_token.gpg"
if [ -f "$TOKEN_FILE" ]; then
    echo "Verificando/Refrescando token OAuth2..."
    # Ejecutamos el script para que refresque el token si es necesario (la salida stdout es el token, la silenciamos)
    python3 mutt_oauth2.py --verbose "$TOKEN_FILE" > /dev/null
else
    echo "AVISO: No se encontró el archivo de token $TOKEN_FILE. Saltando refresco."
fi

# mbsync -a

# 2. Descargar Jira
echo "Descargando tareas de Jira..."
python3 descargar_jira.py

# 3. Procesar y Generar Obsidian
echo "Procesando información y generando Nota Diaria..."
python3 procesar_todo.py

echo "¡Proceso completado! Revisa tu Obsidian."
