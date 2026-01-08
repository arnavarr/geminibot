"""
DataCollector - Script de extracción de datos determinista.

Reemplaza el agente basado en LLM por un script que:
1. Obtiene tareas de Jira
2. Obtiene correos de Outlook
3. Genera JSON estructurado (artifacts/context_payload.json)
4. Crea nota Markdown (artifacts/daily_context.md y Obsidian)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Ensure project root is on sys.path when running this file directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import settings
from src.tools.jira_tools import get_all_my_issues
from src.tools.email_tools import fetch_recent_emails, _get_graph_access_token, _fetch_emails_from_graph, MSAL_AVAILABLE
from src.tools.obsidian_tools import write_daily_note


class DataCollector:
    """
    Recolector de datos determinista para dashboard personal.
    
    Extrae información de Jira y Outlook, genera archivos de contexto
    para uso posterior en conversaciones con LLMs externos.
    """

    def __init__(self):
        self.settings = settings
        self.artifacts_dir = PROJECT_ROOT / "artifacts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📊 DataCollector inicializado")
        print(f"   📁 Artifacts: {self.artifacts_dir}")

    def _get_jira_tasks(self) -> List[Dict[str, Any]]:
        """Obtiene todas las tareas de Jira del usuario actual."""
        print("\n📋 Obteniendo tareas de Jira...")
        tasks = get_all_my_issues()
        return tasks

    def _get_emails(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene correos recientes de Outlook."""
        print("\n📧 Obteniendo correos de Outlook...")
        
        if not MSAL_AVAILABLE:
            print("   ⚠️ MSAL no instalado. Saltando correos.")
            return []
        
        if not self.settings.MS_CLIENT_ID:
            print("   ⚠️ MS_CLIENT_ID no configurado. Saltando correos.")
            return []
        
        try:
            token = _get_graph_access_token()
            if not token:
                print("   ⚠️ No se pudo obtener token de acceso.")
                return []
            
            emails_raw = _fetch_emails_from_graph(token, limit)
            
            # Transform to simpler format
            emails = []
            for email in emails_raw:
                emails.append({
                    "subject": email.get("subject", "(Sin asunto)"),
                    "from": email.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
                    "received": email.get("receivedDateTime"),
                    "preview": email.get("bodyPreview", "")[:200]
                })
            
            print(f"   ✅ Obtenidos {len(emails)} correos")
            return emails
            
        except Exception as e:
            print(f"   ❌ Error obteniendo correos: {e}")
            return []

    def _generate_context_json(self, tasks: List[Dict], emails: List[Dict]) -> Dict[str, Any]:
        """Genera el payload JSON estructurado."""
        payload = {
            "timestamp": datetime.now().isoformat(),
            "generated_by": "DataCollector",
            "jira_tasks": tasks,
            "emails": emails,
            "summary": {
                "total_tasks": len(tasks),
                "total_emails": len(emails),
                "tasks_by_status": self._count_by_field(tasks, "status"),
                "tasks_by_priority": self._count_by_field(tasks, "priority")
            }
        }
        return payload

    def _count_by_field(self, items: List[Dict], field: str) -> Dict[str, int]:
        """Cuenta items por un campo específico."""
        counts: Dict[str, int] = {}
        for item in items:
            value = item.get(field) or "Sin especificar"
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _generate_markdown(self, tasks: List[Dict], emails: List[Dict]) -> str:
        """Genera el contenido Markdown para la nota diaria."""
        today = datetime.now()
        lines = [
            f"# Contexto del día - {today.strftime('%Y-%m-%d')}",
            "",
            f"*Generado automáticamente el {today.strftime('%d/%m/%Y a las %H:%M')}*",
            "",
        ]
        
        # Jira Tasks Section
        lines.append("## 📋 Tareas de Jira")
        lines.append("")
        
        if tasks:
            # Group by status
            by_status: Dict[str, List[Dict]] = {}
            for task in tasks:
                status = task.get("status") or "Sin estado"
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append(task)
            
            for status, status_tasks in by_status.items():
                lines.append(f"### {status} ({len(status_tasks)})")
                lines.append("")
                for task in status_tasks:
                    key = task.get("key", "???")
                    summary = task.get("summary", "Sin resumen")
                    priority = task.get("priority") or "N/A"
                    lines.append(f"- **[{key}]** {summary} *(Prioridad: {priority})*")
                lines.append("")
        else:
            lines.append("*No se encontraron tareas asignadas.*")
            lines.append("")
        
        # Emails Section
        lines.append("## 📧 Correos Recientes")
        lines.append("")
        
        if emails:
            for i, email in enumerate(emails, 1):
                subject = email.get("subject", "(Sin asunto)")
                sender = email.get("from", "Desconocido")
                preview = email.get("preview", "")[:100]
                lines.append(f"{i}. **{subject}**")
                lines.append(f"   - De: {sender}")
                if preview:
                    lines.append(f"   - Vista previa: {preview}...")
                lines.append("")
        else:
            lines.append("*No hay correos no leídos recientes.*")
            lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Este archivo es contexto para usar con Gemini o ChatGPT.*")
        
        return "\n".join(lines)

    def run(self):
        """
        Ejecuta la recolección completa de datos.
        
        1. Obtiene tareas de Jira
        2. Obtiene correos de Outlook
        3. Guarda JSON en artifacts/context_payload.json
        4. Genera nota Markdown
        5. Escribe en Obsidian y artifacts/daily_context.md
        """
        print("\n" + "=" * 60)
        print("🚀 Iniciando recolección de datos...")
        print("=" * 60)
        
        # 1. Collect data
        tasks = self._get_jira_tasks()
        emails = self._get_emails(limit=10)
        
        # 2. Generate JSON payload
        print("\n📦 Generando payload JSON...")
        payload = self._generate_context_json(tasks, emails)
        
        json_path = self.artifacts_dir / "context_payload.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Guardado: {json_path}")
        
        # 3. Generate Markdown
        print("\n📝 Generando nota Markdown...")
        markdown_content = self._generate_markdown(tasks, emails)
        
        # Save to artifacts
        md_path = self.artifacts_dir / "daily_context.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"   ✅ Guardado: {md_path}")
        
        # 4. Write to Obsidian
        if self.settings.OBSIDIAN_VAULT_PATH:
            print("\n📓 Escribiendo en Obsidian...")
            result = write_daily_note(markdown_content)
            print(f"   {result}")
        else:
            print("\n⚠️ OBSIDIAN_VAULT_PATH no configurado. Nota no escrita en Obsidian.")
        
        # 5. Final message
        print("\n" + "=" * 60)
        print("✅ Datos exportados a artifacts/context_payload.json y nota creada en Obsidian.")
        print("=" * 60)


if __name__ == "__main__":
    collector = DataCollector()
    collector.run()
