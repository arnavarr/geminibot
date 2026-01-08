import json
import logging
from typing import Optional

# Importamos el cliente seguro que creamos anteriormente
# Asegúrate de que secure_email_client.py esté en dashboard_bot/src/utils/
try:
    from src.utils.secure_email_client import SecureEmailClient
except ImportError:
    # Fallback por si la estructura de carpetas es diferente durante pruebas
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from src.utils.secure_email_client import SecureEmailClient

# Configuración de logging
logger = logging.getLogger(__name__)

# Instancia global del cliente (para reutilizar el token OAuth y no pedir login en cada llamada)
_email_client_instance = None

def get_email_client():
    """Singleton para mantener la sesión autenticada activa."""
    global _email_client_instance
    if _email_client_instance is None:
        try:
            _email_client_instance = SecureEmailClient()
        except Exception as e:
            logger.error(f"Fallo al inicializar el cliente de correo: {e}")
            raise e
    return _email_client_instance

def send_email(to_email: str, subject: str, body: str) -> str:
    """
    Envía un correo electrónico a un destinatario específico.
    
    Args:
        to_email (str): La dirección de correo del destinatario.
        subject (str): El asunto del correo.
        body (str): El contenido del cuerpo del correo.
    
    Returns:
        str: Mensaje de éxito o error en formato JSON.
    """
    try:
        client = get_email_client()
        success = client.send_email(to_email, subject, body)
        
        if success:
            return json.dumps({"status": "success", "message": f"Correo enviado a {to_email}"})
        else:
            return json.dumps({"status": "error", "message": "Fallo en el envío SMTP. Revisa los logs."})
            
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def read_emails(limit: int = 5) -> str:
    """
    Lee los correos más recientes de la bandeja de entrada.
    
    Args:
        limit (int): Número de correos a recuperar (por defecto 5).
    
    Returns:
        str: Lista de correos en formato JSON con remitente y asunto.
    """
    try:
        client = get_email_client()
        emails = client.fetch_recent_emails(limit=limit)
        
        if not emails:
            return json.dumps({"status": "success", "data": [], "message": "No se encontraron correos nuevos."})
            
        # Formateamos para que sea fácil de leer por el LLM
        return json.dumps({
            "status": "success",
            "count": len(emails),
            "emails": emails
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def search_emails(query: str) -> str:
    """
    (Opcional) Busca correos específicos. 
    Nota: La implementación actual del cliente fetch_recent_emails es básica.
    Para búsquedas avanzadas, se debería extender el cliente.
    """
    return json.dumps({"status": "error", "message": "La búsqueda avanzada no está implementada en esta versión del cliente."})