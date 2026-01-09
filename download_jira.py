import os
import json
import requests
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def download_jira_issues():
    # 1. Configuración
    # El servidor indicó explícitamente usar /search/jql debido al error 410 en /search
    url = 'https://tirea.atlassian.net/rest/api/3/search/jql'
    
    jira_token = os.getenv('JIRA_TOKEN')
    output_file = 'issues.json'

    # Validación básica
    if not jira_token:
        print("Error: No se encontró la variable JIRA_TOKEN en el archivo .env")
        return

    # 2. Preparar Headers
    headers = {
        'Authorization': f'Basic {jira_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # 3. Preparar el Payload
    # CORRECCIÓN: maxResults se ha reducido a 100.
    # Solicitar 1000 suele causar un error 400 (Bad Request) porque supera el límite de la API.
    payload = {
        "jql": "project in (CYB, PRO40, PRO44) ORDER BY created DESC",
        "maxResults": 100, 
        "fields": ["*all"],
        "expand": ["renderedFields", "changelog", "comments"]
    }

    print(f"Conectando a {url}...")

    try:
        # 4. Ejecutar la petición POST
        response = requests.post(url, json=payload, headers=headers)
        
        # Lanzar excepción si hay error HTTP (4xx, 5xx)
        response.raise_for_status()

        # 5. Guardar el resultado en issues.json
        data = response.json()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"¡Éxito! Archivo guardado correctamente en: {output_file}")
        print(f"Total de issues recuperados en esta página: {len(data.get('issues', []))}")

    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP: {http_err}")
        print(f"Código de estado: {response.status_code}")
        try:
            # Intentar mostrar el mensaje de error específico de Jira
            error_response = response.json()
            print(f"Detalles del error (JSON): {json.dumps(error_response, indent=2)}")
        except:
            print(f"Respuesta del servidor (texto): {response.text}")
            
    except Exception as err:
        print(f"Ocurrió un error inesperado: {err}")

if __name__ == "__main__":
    download_jira_issues()