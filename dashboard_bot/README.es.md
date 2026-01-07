# Dashboard Bot

**Objetivo:** Actuar como Asistente Ejecutivo Personal para líderes de equipos de desarrollo.

## Descripción

El Dashboard Bot es un agente inteligente diseñado para optimizar tu rutina matutina. Se conecta a tus herramientas esenciales para:

1. **Consultar Jira** en busca de alertas críticas y tareas pendientes.
2. **Revisar correos no leídos de Outlook** para identificar comunicaciones que requieren atención.
3. **Sintetizar toda la información** en una Nota Diaria perfectamente formateada en Obsidian.

## Características

- **Integración con Jira**: Obtiene problemas de alta prioridad y consultas JQL personalizadas.
- **Integración con Outlook**: Recupera correos electrónicos no leídos de las últimas 24 horas.
- **Soporte para Obsidian**: Genera y anexa automáticamente a las Notas Diarias siguiendo una plantilla específica.
- **Configuración Segura**: Utiliza `.env` para la gestión de credenciales.

## Requisitos Previos

- Python 3.8 o superior
- Git

## Instalación

### Instalación Automática (Linux/macOS)

El instalador incluido configura el entorno virtual, instala las dependencias e inicializa la configuración.

```bash
./install.sh
```

### Instalación Manual (Windows/Linux/macOS)

1. **Clonar el repositorio:**

    ```bash
    git clone <repository-url>
    cd dashboard_bot
    ```

2. **Crear y activar un entorno virtual:**

    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Instalar dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configurar variables de entorno:**
    Copia el archivo de configuración de ejemplo:

    ```bash
    # Windows
    copy .env.example .env

    # Linux/macOS
    cp .env.example .env
    ```

    Abre `.env` y completa tus claves API y rutas:
    - `GOOGLE_API_KEY`: Para Gemini AI.
    - `JIRA_URL`, `JIRA_EMAIL`, `JIRA_TOKEN`: Para acceso a Jira.
    - `MS_CLIENT_ID`, `MS_AUTHORITY`: Para acceso a Outlook.
    - `OBSIDIAN_VAULT_PATH`: Ruta absoluta a tu bóveda de Obsidian.

## Uso

Asegúrate de que tu entorno virtual esté activado, luego ejecuta el agente con una tarea en lenguaje natural:

```bash
python agent.py "Create today's daily note with my Jira tasks and emails"
```

(O en español, si el agente está configurado para entenderlo, aunque el comando por defecto es en inglés)

O simplemente:

```bash
python agent.py
```

(Por defecto ejecuta la tarea de resumen diario estándar)

## Estructura del Proyecto

- `src/`: Lógica central del agente y herramientas.
- `tests/`: Pruebas unitarias y de integración.
- `openspec/`: Definiciones de OpenSpec.
- `artifacts/`: Salidas generadas.
- `agent.py`: Script de punto de entrada.

## Contribución

Las solicitudes de extracción (pull requests) son bienvenidas. Para cambios importantes, por favor abre un problema (issue) primero para discutir lo que te gustaría cambiar.

## Licencia

[MIT](https://choosealicense.com/licenses/mit/)
