#!/bin/bash

# Script de inicio de día: Sincronización y Procesamiento

# 1. Sincronizar correo
# Asumimos que mbsync está configurado. Descomentar si es necesario.
# echo "Sincronizando correos..."
# 
# 1.1 Refrescar Token OAuth2 (Microsoft)
# Buscamos el token en el directorio actual o en el home
TOKEN_FILE="microsoft.token"
USER_HOME_TOKEN="$HOME/microsoft.token"

if [ -f "$TOKEN_FILE" ]; then
    TARGET_TOKEN="$TOKEN_FILE"
elif [ -f "$USER_HOME_TOKEN" ]; then
    TARGET_TOKEN="$USER_HOME_TOKEN"
else
    TARGET_TOKEN=""
fi

if [ -n "$TARGET_TOKEN" ]; then
    echo "Verificando/Refrescando token OAuth2 ($TARGET_TOKEN)..."
    python3 mutt_oauth2.py --verbose "$TARGET_TOKEN" > /dev/null
else
    echo "AVISO: No se encontró 'microsoft.token' en . ni en $HOME. Saltando refresco."
fi

# mbsync -a

# 2. Descargar Jira
echo "Descargando tareas de Jira..."
python3 descargar_jira.py

# 3. Procesar y Generar Obsidian
echo "Procesando información y generando Nota Diaria..."
python3 procesar_todo.py

echo "¡Proceso completado! Revisa tu Obsidian."
