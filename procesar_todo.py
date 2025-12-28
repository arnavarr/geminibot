import json
import mailbox
import email
from email.policy import default
from datetime import datetime
from pathlib import Path
import re
import os
import html
from dotenv import load_dotenv

# --- Configuración ---
load_dotenv() # Cargar variables de entorno

DATA_DIR = Path("data")
JIRA_FILE = DATA_DIR / "tareas_jira.json"
PROCESSED_EMAILS_FILE = DATA_DIR / "processed_emails.json"

# Rutas configurables via .env (con defaults)
MAIL_DIR_PATH = Path(os.getenv("MAIL_DIR_PATH", Path.home() / "Maildir"))
OBSIDIAN_VAULT_PATH = Path(os.getenv("OBSIDIAN_VAULT_PATH", "/mnt/c/Users/arturonavarro/ObsidianVault"))

DAILY_NOTES_PATH = OBSIDIAN_VAULT_PATH / "Daily Notes"
GDS_PATH = OBSIDIAN_VAULT_PATH / "GDS" / "Guias"

if not OBSIDIAN_VAULT_PATH.exists():
    print(f"[ADVERTENCIA] La ruta del Vault no existe o no es accesible: {OBSIDIAN_VAULT_PATH}")
    print("[ADVERTENCIA] Por favor, configura OBSIDIAN_VAULT_PATH en el archivo .env")

# --- Funciones ---

def load_processed_ids():
    """Carga los IDs de correos ya procesados desde el JSON."""
    if not PROCESSED_EMAILS_FILE.exists():
        return set()
    try:
        with open(PROCESSED_EMAILS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except Exception as e:
        print(f"[ERROR] No se pudo leer {PROCESSED_EMAILS_FILE}: {e}")
        return set()

def save_processed_ids(ids):
    """Guarda los IDs de correos procesados en el JSON."""
    try:
        with open(PROCESSED_EMAILS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(ids), f, indent=4)
        print(f"[INFO] Se actualizaron los IDs procesados en {PROCESSED_EMAILS_FILE}")
    except Exception as e:
        print(f"[ERROR] No se pudo guardar {PROCESSED_EMAILS_FILE}: {e}")

def load_jira_data(filepath):
    """Carga las tareas de Jira desde el JSON."""
    if not filepath.exists():
        print(f"[ADVERTENCIA] No se encontró {filepath}")
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Error al leer {filepath}: {e}")
        return []

def clean_html(raw_html):
    """Limpia etiquetas HTML básicas y entidades."""
    if not raw_html:
        return ""
    # Quitar tags
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    # Decodificar entidades (&nbsp;, &gt;, etc.)
    return html.unescape(cleantext).strip()

def load_emails(maildir_path, processed_ids):
    """Lee correos nuevos del Maildir, ignorando los ya procesados."""
    emails = []
    if not maildir_path.exists():
        print(f"[ADVERTENCIA] No se encontró Maildir en {maildir_path}")
        return []

    processed_count = 0
    skipped_count = 0
    
    # Abrir Maildir
    mbox = mailbox.Maildir(maildir_path)
    
    for message in mbox:
        try:
            msg = email.message_from_bytes(message.as_bytes(), policy=default)
            msg_id = msg["message-id"]
            
            if msg_id and msg_id in processed_ids:
                skipped_count += 1
                continue

            subject = msg["subject"] or "(Sin Asunto)"
            sender = msg["from"] or "(Desconocido)"
            
            body = ""
            if msg.is_multipart():
                # Prioridad: text/plain -> text/html
                found_body = False
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        try:
                            body = part.get_content()
                            found_body = True
                            break
                        except Exception as e:
                            print(f"[ERROR] Fallo al decodificar body text/plain: {e}")
                
                if not found_body:
                    for part in msg.walk():
                        if part.get_content_type() == "text/html":
                            try:
                                html_content = part.get_content()
                                body = clean_html(html_content)
                                found_body = True
                                break
                            except Exception as e:
                                print(f"[ERROR] Fallo al decodificar body text/html: {e}")
            else:
                try:
                    content_type = msg.get_content_type()
                    content = msg.get_content()
                    if content_type == "text/html":
                        body = clean_html(content)
                    else:
                        body = content
                except Exception as e:
                     print(f"[ERROR] Fallo al decodificar mensaje simple: {e}")
            
            if not body:
                body = "(No se pudo extraer el contenido del mensaje)"

            emails.append({
                "message_id": msg_id,
                "sender": sender,
                "subject": subject,
                "body": body,
                "date": msg["date"]
            })
            processed_count += 1
            
        except Exception as e:
            print(f"[ERROR] Error procesando un mensaje: {e}")
            continue

    print(f"[INFO] Correos procesados: {processed_count}, Saltados (ya procesados): {skipped_count}")
    return emails

def generate_gds_file(item, type_source):
    """Genera un archivo Markdown en GDS si cumple criterios."""
    if type_source == "jira":
        # Logica original: ignorar Jira para GDS por ahora
        pass

    elif type_source == "email":
        content = item.get("body", "")
        summary = item.get("subject", "")
        
        keywords = ["Guía", "Normativa", "Manual"]
        if any(k.lower() in (summary + content).lower() for k in keywords):
            filename = f"GDS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = GDS_PATH / filename
            
            if not GDS_PATH.exists():
                GDS_PATH.mkdir(parents=True, exist_ok=True)
                
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# {summary}\n\n")
                    f.write(f"**Remitente:** {item.get('sender')}\n")
                    f.write(f"**Fecha:** {item.get('date')}\n\n")
                    f.write(content)
                print(f"[INFO] Generado GDS: {filepath}")
            except Exception as e:
                print(f"[ERROR] No se pudo escribir GDS {filepath}: {e}")

def get_existing_content(filepath):
    """Lee el contenido de una nota diaria existente para control de duplicados."""
    if not filepath.exists():
        return ""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[ERROR] No se pudo leer nota diaria {filepath}: {e}")
        return ""

def main():
    print("[INFO] Iniciando procesamiento...")
    
    # Cargar datos
    processed_ids = load_processed_ids()
    jira_tasks = load_jira_data(JIRA_FILE)
    email_list = load_emails(MAIL_DIR_PATH, processed_ids)
    
    # Estructuras para Daily Note
    cuestionarios_items = []
    vuln_items = []
    gds_alerts = []
    alerts_crit = []
    
    new_processed_ids = set()

    # Prepara chequeo de duplicados
    today = datetime.now().strftime("%Y-%m-%d")
    md_file = DAILY_NOTES_PATH / f"{today}.md"
    existing_content = get_existing_content(md_file)

    # Procesar Jira
    count_jira = 0
    for issue in jira_tasks:
        fields = issue.get("fields", {})
        project = fields.get("project", {}).get("key", "")
        summary = fields.get("summary", "")
        status = fields.get("status", {}).get("name", "")
        priority = fields.get("priority", {}).get("name", "")
        key = issue.get("key", "") # Ejemplo: PROJ-123
        
        # Check duplicado en archivo existente usando la Key o Summary
        duplicate_check_str = f"[{project}] {summary}" # Lo que se usa en display_text
        if key in existing_content or duplicate_check_str in existing_content:
            # Si la key (e.g. OD-42) ya sale, asumimos que está. 
            # Ojo: si el formato es "- [ ] [OD] Tarea...", buscar "Tarea" es seguro.
            continue
            
        display_text = f"[{project}] {summary} ({status})"
        
        # Clasificación
        item_line = ""
        is_critical = False
        
        if project in ["OD", "ODC"]:
            item_line = f"- [ ] {display_text}"
            cuestionarios_items.append(item_line)
        elif project in ["VI", "VUL", "CYB", "OSO1GD"]:
            item_line = f"- [ ] {display_text}"
            vuln_items.append(item_line)
            if project in ["VUL", "CYB"] and priority in ["High", "Highest", "Critical"]:
                crit_line = f"- [!] CRITICO: {display_text}"
                if crit_line not in existing_content:
                    alerts_crit.append(crit_line)
        else:
            item_line = f"- [ ] {display_text} (Otros)"
            cuestionarios_items.append(item_line)
        
        count_jira += 1

    # Procesar Emails
    count_email = 0
    for email_item in email_list:
        subj = email_item["subject"]
        sender = email_item["sender"]
        msg_id = email_item.get("message_id")
        
        # Check GDS
        generate_gds_file(email_item, "email")
        
        # Check duplicado
        # Buscamos el asunto en el contenido existente
        if subj in existing_content:
            # Ya existe algo con este asunto
            if msg_id:
                new_processed_ids.add(msg_id)
            continue

        line = f"- [ ] 📧 Revisar: {subj} (De: {sender})"
        cuestionarios_items.append(line)
        
        if msg_id:
            new_processed_ids.add(msg_id)
        count_email += 1

    if count_jira == 0 and count_email == 0:
        print("[INFO] No hay nuevos ítems para añadir.")
        # Igual guardamos IDs si hubo correos procesados (aunque no añadidos a la nota, pero leidos)
        # En este flujo, si no se añaden a la nota (por duplicado), igual deberíamos marcarlos como procesados?
        # El prompt dice: "Skip emails that have already been processed".
        # Si estan en el existing_content, es que ya fueron procesados ayer u hoy antes?
        # Si estan en existing_content pero NO en processed_ids (ej. borré el json), debería agregarlos a processed_ids.
        # Por seguridad, guardamos los de esta tanda.
    
    # Actualizar DB de ids
    if new_processed_ids:
        all_ids = processed_ids.union(new_processed_ids)
        save_processed_ids(all_ids)

    # Si no hay nada nuevo que escribir, salimos (o creamos archivo vacio si no existe)
    if not cuestionarios_items and not vuln_items and not alerts_crit and md_file.exists():
        print(f"[INFO] Nota diaria {md_file} ya existe y no hay info nueva.")
        return

    # Generar Markdown (Append o Create)
    if not DAILY_NOTES_PATH.exists():
        DAILY_NOTES_PATH.mkdir(parents=True, exist_ok=True)
        
    mode = "a" if md_file.exists() else "w"
    
    # Si es append, añadimos un separador de hora
    timestamp_header = f"\n\n### Actualización: {datetime.now().strftime('%H:%M')}\n" if mode == "a" else ""
    
    # Si el archivo es nuevo, construimos estructura completa. Si es append, solo lo nuevo.
    # Pero el usuario pidió: "Compare... Only append new items".
    # Lo más limpio si es append es agregar bloque "Actualización" o simplemente agregar a las listas si pudieramos parsear el md.
    # Como es un script simple, si es 'a', agregaremos bloques adicionales.
    
    if mode == "w":
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
    else:
        # Modo Append
        # Solo escribimos si hay algo nuevo
        if not (alerts_crit or cuestionarios_items or vuln_items):
            print("[INFO] Procesado completado. Sin novedades.")
            return

        md_content = timestamp_header
        if alerts_crit:
            md_content += "\n#### Nuevas Alertas Críticas\n" + "\n".join(alerts_crit) + "\n"
        if cuestionarios_items:
            md_content += "\n#### Nuevos Cuestionarios/Correos\n" + "\n".join(cuestionarios_items) + "\n"
        if vuln_items:
            md_content += "\n#### Nuevas Vulnerabilidades\n" + "\n".join(vuln_items) + "\n"

    try:
        with open(md_file, mode, encoding="utf-8") as f:
            f.write(md_content)
        print(f"[INFO] Nota diaria actualizada: {md_file}")
    except Exception as e:
        print(f"[ERROR] No se pudo escribir en {md_file}: {e}")

if __name__ == "__main__":
    main()
