import os
import json
import requests
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def download_jira_issues():
    # 1. Configuración
    # Usamos /search/jql ya que /search devolvió 410 (Gone)
    url = 'https://tirea.atlassian.net/rest/api/3/search/jql'
    
    jira_token = os.getenv('JIRA_TOKEN')
    
    # Configurar ruta de salida usando ARTIFACTS_DIR
    artifacts_dir = os.getenv('ARTIFACTS_DIR', '.')
    output_file = os.path.join(artifacts_dir, 'issues.json')

    if not jira_token:
        print("Error: No se encontró la variable JIRA_TOKEN en el archivo .env")
        return

    # 2. Preparar Headers
    headers = {
        'Authorization': f'Basic {jira_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # 3. Preparar el Payload (Simplificado para evitar Error 400)
    # Hemos eliminado "expand" y cambiado "fields" por una lista explícita.
    # "*all" a menudo causa errores de validación en este endpoint.
    payload = {
        "jql": "project in (CYB, PRO40, PRO44) ORDER BY created DESC",
        "maxResults": 50, # Reducido a 50 para asegurar estabilidad
        "fields": [
            "summary", 
            "status", 
            "created", 
            "priority", 
            "assignee", 
            "description"
        ]
        # Si el script funciona, puedes probar a descomentar la siguiente línea:
        # "expand": ["changelog", "comments"] 
    }

    print(f"Conectando a {url}...")
    # Debug: Imprimir lo que vamos a enviar (útil para diagnosticar el error 400)
    print(f"Enviando payload: {json.dumps(payload)}")

    try:
        response = requests.post(url, json=payload, headers=headers)
        
        response.raise_for_status()

        data = response.json()
        
        # Verificar si Jira nos devolvió advertencias sobre el JQL
        if 'warningMessages' in data and data['warningMessages']:
            print("\n--- ADVERTENCIAS DE JIRA ---")
            for warning in data['warningMessages']:
                print(f"⚠️  {warning}")
            print("------------------------------\n")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        issues_count = len(data.get('issues', []))
        print(f"¡Éxito! Archivo guardado en: {output_file}")
        print(f"Total de issues recuperados: {issues_count}")

        if issues_count == 0:
            print("\n[DIAGNOSTICO] La búsqueda no arrojó resultados.")
            print("Sugiero probar temporalmente un JQL más amplio para verificar permisos.")
            print("Ejemplo: Cambia 'jql' en el código a simplemente 'order by created DESC'")

    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP: {http_err}")
        print(f"Código: {response.status_code}")
        try:
            print(f"Detalles del error: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Respuesta cruda: {response.text}")
            
    except Exception as err:
        print(f"Error inesperado: {err}")

if __name__ == "__main__":
    download_jira_issues()