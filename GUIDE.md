# Guía de Configuración y Uso

## 1. Requisitos Previos

- Python 3.x instalado.
- Acceso a Internet para conectar con Jira.
- Credenciales de Jira (Token y Email) configuradas en el script `descargar_jira.py`.

## 2. Instalación de Dependencias

Ejecuta el siguiente comando para instalar las librerías necesarias:

```bash
pip install -r requirements.txt
```

## 3. Configuración

### Variables de Entorno (Jira)
El proyecto utiliza un archivo `.env` para gestionar las credenciales.
1. Copia el archivo de ejemplo:
   ```bash
   cp .env.example .env
   ```
2. Edita `.env` y añade tus datos:
   - **JIRA_EMAIL**: Tu correo.
   - **JIRA_TOKEN**: Tu token de Atlassian.
   - **JIRA_URL**: URL de tu instancia Jira.

### OAuth2 (Correo Microsoft)
El sistema utiliza `mutt_oauth2.py` para gestionar el acceso al correo.
1. Debes crear el archivo de token inicial cifrado (ej. `microsoft_token.gpg`).
2. Ejecuta el script por primera vez para autorizar:
   ```bash
   python mutt_oauth2.py --authorize --verbose microsoft_token.gpg
   ```
   Sigue las instrucciones en pantalla para autenticarte en el navegador.

### Rutas
Los scripts están configurados para ejecutarse desde la raíz del proyecto.
- Los datos de Jira se guardarán en `data/tareas_jira.json`.
- La nota diaria se generará en la ruta especificada en `procesar_todo.py`.

## 4. Ejecución

### Manualmente
1. Descargar tareas de Jira:
   ```bash
   python descargar_jira.py
   ```
2. Procesar todo y generar nota:
   ```bash
   python procesar_todo.py
   ```

### Automáticamente
Ejecuta el script `iniciar_dia.sh` (asegúrate de darle permisos de ejecución con `chmod +x iniciar_dia.sh`):

```bash
./iniciar_dia.sh
```
