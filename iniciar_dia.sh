#!/bin/bash

# Script de inicio de día: Sincronización y Procesamiento

# Verificación de archivo .env
if [ ! -f ".env" ]; then
    printf "ERROR CRÍTICO: No se encuentra el archivo .env. Deteniendo ejecución.\n"
    exit 1
fi

# Directorio de logs
mkdir -p data
LOG_FILE="data/error.log"

# 1. Sincronizar correo
printf "====================\n1. Sincronización de Correo (OAuth2)\n====================\n"

# Asumimos que mbsync está configurado. Descomentar si es necesario.
# printf "Sincronizando correos...\n"

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
    printf "Verificando/Refrescando token OAuth2 ($TARGET_TOKEN)...\n"
    python3 mutt_oauth2.py --verbose "$TARGET_TOKEN" > /dev/null 2>> "$LOG_FILE"
else
    printf "AVISO: No se encontró 'microsoft.token' en . ni en $HOME. Saltando refresco.\n"
fi

# mbsync -a

# 2. Descargar Jira
printf "\n====================\n2. Descarga de Jira\n====================\n"
printf "Descargando tareas de Jira...\n"
python3 descargar_jira.py 2>> "$LOG_FILE"

# 3. Procesar y Generar Obsidian
printf "\n====================\n3. Procesamiento y Obsidian\n====================\n"
printf "Procesando información y generando Nota Diaria...\n"
python3 procesar_todo.py 2>> "$LOG_FILE"

printf "\n====================\n¡Proceso completado! Revisa tu Obsidian.\n====================\n"
