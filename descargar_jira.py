import requests
from requests.auth import HTTPBasicAuth
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")

if not all([JIRA_URL, JIRA_EMAIL, JIRA_TOKEN]):
    print("Error: Faltan variables de entorno. Asegúrate de configurar el archivo .env")
    exit(1)

# Ruta de salida
OUTPUT_DIR = Path("data")
OUTPUT_FILE = OUTPUT_DIR / "tareas_jira.json"

def descargar_tareas():
    print("Conectando con Jira...")
    
    url = f"{JIRA_URL}/rest/api/3/search"
    
    # JQL Query
    jql = (
        'project IN (OD, ODC, PRO40, PRO44, VI, VUL, OSO1GD, CYB) '
        'AND (team IN ("Cuestionarios", "Gestión de vulnerabilidades") '
        'OR component IN ("Cuestionarios", "Gestión de vulnerabilidades")) '
        'AND status != "Done"'
    )
    
    # Campos a extraer
    fields = [
        "summary",
        "status",
        "assignee",
        "priority",
        "duedate",
        "description",
        "project",
        "comment" # 'comment' is usually getting comments
    ]

    params = {
        "jql": jql,
        "fields": fields,
        "maxResults": 100 # Adjust if necessary
    }

    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    headers = {
        "Accept": "application/json"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            auth=auth
        )
        
        response.raise_for_status()
        
        data = response.json()
        issues = data.get("issues", [])
        
        print(f"Se encontraron {len(issues)} tareas.")
        
        # Guardar en local
        if not OUTPUT_DIR.exists():
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(issues, f, ensure_ascii=False, indent=4)
            
        print(f"Tareas guardadas exitosamente en {OUTPUT_FILE}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con Jira: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Respuesta del servidor: {e.response.text}")

if __name__ == "__main__":
    descargar_tareas()
