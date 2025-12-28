import requests
from requests.auth import HTTPBasicAuth
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import sys

# Cargar variables de entorno
load_dotenv()

# Configuración
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")

if not all([JIRA_URL, JIRA_EMAIL, JIRA_TOKEN]):
    print("Error: Faltan variables de entorno. Asegúrate de configurar el archivo .env")
    sys.exit(1)

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
    
    # Campos a extraer (sin 'comment', asegurando 'priority', 'status', 'summary', 'updated')
    fields = [
        "summary",
        "status",
        "assignee",
        "priority",
        "duedate",
        "description",
        "project",
        "updated"
    ]

    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    headers = {
        "Accept": "application/json"
    }

    all_issues = []
    start_at = 0
    max_results = 50 # Tamaño del lote
    total = 1 # Valor inicial para entrar al bucle

    print(f"Iniciando descarga de tareas...")

    while start_at < total:
        params = {
            "jql": jql,
            "fields": fields,
            "startAt": start_at,
            "maxResults": max_results
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                auth=auth,
                timeout=30 # Timeout razonable
            )
            
            response.raise_for_status()
            
            try:
                data = response.json()
            except json.decoder.JSONDecodeError as e:
                print(f"Error al decodificar la respuesta JSON: {e}")
                print(f"Contenido de la respuesta: {response.text[:200]}...") # Mostrar inicio de la respuesta
                break # Detener si no podemos leer la respuesta

            issues_batch = data.get("issues", [])
            total = data.get("total", 0)
            
            if not issues_batch:
                print("No se encontraron más tareas en este lote.")
                break

            all_issues.extend(issues_batch)
            
            # Feedback visual de progreso
            end_at = min(start_at + max_results, total)
            print(f"Procesando tareas {start_at + 1} a {end_at} de {total}...")
            
            start_at += len(issues_batch)

        except requests.exceptions.ConnectionError:
            print("Error de conexión: No se pudo conectar al servidor de Jira.")
            break
        except requests.exceptions.Timeout:
            print("Error: La solicitud a Jira ha excedido el tiempo de espera.")
            break
        except requests.exceptions.RequestException as e:
            print(f"Error inesperado al conectar con Jira: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Respuesta del servidor: {e.response.text}")
            break
        except Exception as e:
            print(f"Ocurrió un error inesperado loop: {e}")
            break

    print(f"\nDescarga finalizada. Total de tareas recolectadas: {len(all_issues)}")
    
    # Guardar en local solo si tenemos datos
    if all_issues:
        if not OUTPUT_DIR.exists():
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            
        try:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_issues, f, ensure_ascii=False, indent=4)
            print(f"Tareas guardadas exitosamente en {OUTPUT_FILE}")
        except IOError as e:
            print(f"Error al guardar el archivo: {e}")
    else:
        print("No se guardaron tareas debido a errores o falta de resultados.")

if __name__ == "__main__":
    descargar_tareas()
