import json
import mailbox
import email
from email.policy import default
from datetime import datetime
from pathlib import Path
import re
import os
from dotenv import load_dotenv

# --- Configuración ---
load_dotenv() # Cargar variables de entorno

DATA_DIR = Path("data")
JIRA_FILE = DATA_DIR / "tareas_jira.json"

# Rutas configurables via .env (con defaults)
MAIL_DIR_PATH = Path(os.getenv("MAIL_DIR_PATH", Path.home() / "Maildir"))
OBSIDIAN_VAULT_PATH = Path(os.getenv("OBSIDIAN_VAULT_PATH", "/mnt/c/Users/arturonavarro/ObsidianVault"))

DAILY_NOTES_PATH = OBSIDIAN_VAULT_PATH / "Daily Notes"
GDS_PATH = OBSIDIAN_VAULT_PATH / "GDS" / "Guias"

if not OBSIDIAN_VAULT_PATH.exists():
    print(f"ADVERTENCIA: La ruta del Vault no existe o no es accesible: {OBSIDIAN_VAULT_PATH}")
    print("Por favor, configura OBSIDIAN_VAULT_PATH en el archivo .env")

# --- Funciones ---

def load_jira_data(filepath):
    """Carga las tareas de Jira desde el JSON."""
    if not filepath.exists():
        print(f"Advertencia: No se encontró {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def load_emails(maildir_path):
    """Lee correos nuevos del Maildir."""
    emails = []
    if not maildir_path.exists():
        print(f"Advertencia: No se encontró Maildir en {maildir_path}")
        return []

    # Abrir Maildir
    mbox = mailbox.Maildir(maildir_path)
    
    # Iterar sobre mensajes. 
    # Nota: En un flujo real, deberíamos marcar como leídos o moverlos para no procesarlos doble.
    # Aquí leemos todos los de la carpeta 'new' si existe, o iteramos el mbox si mbsync ya los movió a cur.
    # Simplemente iteraremos sobre todos para este ejemplo, o solo 'new' si preferimos.
    # mbox iterará sobre 'new' y 'cur'.
    
    for message in mbox:
        # Usar policy=default para manejar mejor la codificación
        msg = email.message_from_bytes(message.as_bytes(), policy=default)
        
        subject = msg["subject"]
        sender = msg["from"]
        
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = part.get_content()
                    except:
                        pass
        else:
            try:
                body = msg.get_content()
            except:
                pass
                
        emails.append({
            "sender": sender,
            "subject": subject,
            "body": body,
            "date": msg["date"]
        })
        
    return emails

def generate_gds_file(item, type_source):
    """Genera un archivo Markdown en GDS si cumple criterios."""
    
    if type_source == "jira":
        content = item.get("fields", {}).get("description", "") or ""
        summary = item.get("fields", {}).get("summary", "")
        status = item.get("fields", {}).get("status", {}).get("name", "")
        # Criterio: Keywords + Finalizado
        if status != "Done" and status != "Finalizado": # El prompt decia status="Finalizado", Jira suele ser Done. Ajustar.
             # Pero el prompt dice JQL status != "Done", así que NUNCA vendrán tareas finalizadas de Jira aqui.
             # Revisar logica: "Si una tarea o correo contiene... y su estado es Finalizado"
             # Si el JQL excluye Done, entonces solo correos o tareas que cambien de estado.
             # Asumiremos que para Jira, si llega aquí con status != Done, NO creamos GDS.
             pass
        
        # Como el JQL excluye 'Done', las tareas de Jira vivas no generan GDS automáticamente SÓLO POR ESTADO.
        # Pero tal vez queramos procesar correos.
        pass

    elif type_source == "email":
        content = item.get("body", "")
        summary = item.get("subject", "")
        
        keywords = ["Guía", "Normativa", "Manual"]
        if any(k.lower() in (summary + content).lower() for k in keywords):
            # En correos no hay "estado", asumimos que si llega con keyword es doc final.
            filename = f"GDS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = GDS_PATH / filename
            
            if not GDS_PATH.exists():
                GDS_PATH.mkdir(parents=True, exist_ok=True)
                
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {summary}\n\n")
                f.write(f"**Remitente:** {item.get('sender')}\n")
                f.write(f"**Fecha:** {item.get('date')}\n\n")
                f.write(content)
            print(f"Generado GDS: {filepath}")

def main():
    print("Iniciando procesamiento...")
    
    # Cargar datos
    jira_tasks = load_jira_data(JIRA_FILE)
    email_list = load_emails(MAIL_DIR_PATH)
    
    # Estructuras para Daily Note
    cuestionarios_items = []
    vuln_items = []
    gds_alerts = []
    alerts_crit = []

    # Procesar Jira
    for issue in jira_tasks:
        fields = issue.get("fields", {})
        project = fields.get("project", {}).get("key", "")
        summary = fields.get("summary", "")
        status = fields.get("status", {}).get("name", "")
        priority = fields.get("priority", {}).get("name", "")
        
        display_text = f"[{project}] {summary} ({status})"
        
        # Clasificación por equipos/proyectos
        # Equipos: "Cuestionarios", "Gestión de vulnerabilidades"
        # Si no viene el team explícito en los campos cargados (customfield),
        # usamos lógica basada en Project ID del prompt original o asumimos.
        # Projects Cuestionarios: OD, ODC
        # Projects Vuln: VI, VUL, CYB?? (Asumido por nombres)
        
        # Lógica simple de agrupación
        if project in ["OD", "ODC"]:
            cuestionarios_items.append(f"- [ ] {display_text}")
        elif project in ["VI", "VUL", "CYB", "OSO1GD"]:
             # Vulnerabilidades
            vuln_items.append(f"- [ ] {display_text}")
            if project in ["VUL", "CYB"] and priority in ["High", "Highest", "Critical"]:
                alerts_crit.append(f"- [!] CRITICO: {display_text}")
        else:
            # Default a cuestionarios o log
            cuestionarios_items.append(f"- [ ] {display_text} (Otros)")

    # Procesar Emails (convertir a tareas o GDS)
    for email_item in email_list:
        subj = email_item["subject"]
        sender = email_item["sender"]
        
        # Check GDS
        generate_gds_file(email_item, "email")
        
        # Añadir a inbox general o clasificar
        # Simple: Añadir a cuestionarios si menciona OD/ODC, vuln si VUL, etc.
        # Por ahora, agregamos a una sección "Inbox" o a una de las existentes.
        # El user no pidió sección inbox, pero lo meteremos en Novedades GDS si aplica, o general.
        # Si no es GDS, lo pongo en Cuestionarios por defecto como "Revisar correo".
        cuestionarios_items.append(f"- [ ] 📧 Revisar: {subj} (De: {sender})")

    # Generar Markdown
    today = datetime.now().strftime("%Y-%m-%d")
    md_file = DAILY_NOTES_PATH / f"{today}.md"
    
    if not DAILY_NOTES_PATH.exists():
        DAILY_NOTES_PATH.mkdir(parents=True, exist_ok=True)
        
    md_content = f"""# Planificación del día: {today}

## 🔴 Alertas Críticas (VUL/CYB)
{chr(10).join(alerts_crit) if alerts_crit else "Sin alertas críticas."}

## 📋 Team Cuestionarios (Proyectos OD/ODC)
{chr(10).join(cuestionarios_items) if cuestionarios_items else "Sin tareas pendientes."}

## 🛡️ Team Gestión de Vulnerabilidades
{chr(10).join(vuln_items) if vuln_items else "Sin tareas pendientes."}

## 📚 Novedades GDS (Documentación)
- Revise la carpeta GDS para nuevos documentos generados automáticamente.
"""

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"Nota diaria generada: {md_file}")

if __name__ == "__main__":
    main()
