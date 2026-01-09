import os
import json
import requests
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def download_jira_issues():
    # 1. Configuración
    # CORRECCIÓN: La URL estándar de Jira para búsquedas POST es /rest/api/3/search
    # La URL anterior /rest/api/3/search/jql causaba error 400 por payload inválido.
    url = 'https://tirea.atlassian.net/rest/api/3/search'
    
    jira_token = os.getenv('JIRA_TOKEN')
    output_file = 'issues.json'

    # Validación básica
    if not jira_token:
        print("Error: No se encontró la variable JIRA_TOKEN en el archivo .env")
        return

    # 2. Preparar Headers (equivalente a -H)
    # Se asume que JIRA_TOKEN ya es la cadena codificada en Base64 si el curl usa 'Basic JIRA_TOKEN'
    # Si JIRA_TOKEN es solo el API token, habría que codificarlo (email:token) en base64 aquí.
    headers = {
        'Authorization': f'Basic {jira_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # 3. Preparar el Payload (Data - equivalente a --data)
    payload = {
        "jql": "project in (CYB, PRO40, PRO44) ORDER BY created DESC",
        "maxResults": 1000,
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
            # indent=4 hace que el JSON sea legible para humanos
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"¡Éxito! Archivo guardado correctamente en: {output_file}")

    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP: {http_err}")
        print(f"Respuesta del servidor: {response.text}")
    except Exception as err:
        print(f"Ocurrió un error inesperado: {err}")

if __name__ == "__main__":
    download_jira_issues()