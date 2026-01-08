import smtplib
import imaplib
import email
import ssl
import os
import logging
import time
import base64
import getpass
from email.message import EmailMessage
from typing import List, Dict, Optional

# Intentamos importar MSAL para OAuth, si no está, manejamos el error
try:
    import msal
except ImportError:
    msal = None

logger = logging.getLogger(__name__)

class SecureEmailClient:
    """
    Cliente de correo híbrido: Soporta Autenticación Básica (Legacy) y 
    Autenticación Moderna (OAuth2 / Device Code Flow) para Azure/Office 365.
    """

    def __init__(self):
        # Configuración básica
        self.email_account = os.getenv("EMAIL_ACCOUNT")
        self.auth_method = os.getenv("AUTH_METHOD", "basic").lower() # 'basic' o 'azure_oauth'
        
        # Servidores (Por defecto Outlook para OAuth, Gmail para Basic)
        if self.auth_method == "azure_oauth":
            self.imap_host = os.getenv("EMAIL_HOST_IMAP", "outlook.office365.com")
            self.smtp_host = os.getenv("EMAIL_HOST_SMTP", "smtp.office365.com")
        else:
            self.imap_host = os.getenv("EMAIL_HOST_IMAP", "imap.gmail.com")
            self.smtp_host = os.getenv("EMAIL_HOST_SMTP", "smtp.gmail.com")

        self.imap_port = int(os.getenv("EMAIL_PORT_IMAP", "993"))
        self.smtp_port = int(os.getenv("EMAIL_PORT_SMTP", "587")) # SMTP OAuth suele usar STARTTLS en 587

        # Estado de autenticación
        self.access_token = None
        self.password = None

        if not self.email_account:
            self.email_account = input("Introduce tu dirección de correo electrónico: ").strip()

        # Iniciar proceso de autenticación según método
        if self.auth_method == "azure_oauth":
            self._authenticate_via_azure_oauth()
        else:
            self._authenticate_via_password()

    def _authenticate_via_password(self):
        """Flujo clásico de contraseña."""
        self.password = os.getenv("EMAIL_PASSWORD")
        if not self.password:
            print(f"🔐 Autenticación Básica para: {self.email_account}")
            self.password = getpass.getpass("Introduce tu contraseña (o App Password): ")

    def _authenticate_via_azure_oauth(self):
        """Flujo moderno de OAuth2 Device Code para Azure."""
        if not msal:
            raise ImportError("La librería 'msal' es necesaria para Azure OAuth. Instala con: pip install msal")

        client_id = os.getenv("AZURE_CLIENT_ID")
        tenant_id = os.getenv("AZURE_TENANT_ID")

        if not client_id or not tenant_id:
            raise ValueError("Faltan AZURE_CLIENT_ID o AZURE_TENANT_ID en el entorno.")

        # Scopes necesarios para IMAP y SMTP en Office 365
        scopes = [
            "https://outlook.office.com/IMAP.AccessAsUser.All",
            "https://outlook.office.com/SMTP.Send",
            "User.Read",
            "offline_access" # Para obtener refresh token
        ]

        authority_url = f"https://login.microsoftonline.com/{tenant_id}"
        
        # Caché de tokens simple (en memoria para este ejemplo, idealmente en archivo seguro)
        app = msal.PublicClientApplication(
            client_id, 
            authority=authority_url
        )

        result = None
        accounts = app.get_accounts(username=self.email_account)
        
        # 1. Intentar silenciosamente si ya hay token
        if accounts:
            logger.info("Cuenta encontrada en caché, intentando adquirir token silenciosamente...")
            result = app.acquire_token_silent(scopes, account=accounts[0])

        # 2. Si no, iniciar Device Flow
        if not result:
            flow = app.initiate_device_flow(scopes=scopes)
            if "user_code" not in flow:
                raise RuntimeError(f"Fallo al iniciar Device Flow: {flow.get('error_description')}")

            print("\n" + "="*60)
            print("🚀 AUTENTICACIÓN REQUERIDA CON MICROSOFT AZURE")
            print("="*60)
            print(f"1. Abre esta URL en tu navegador: {flow['verification_uri']}")
            print(f"2. Introduce este código: {flow['user_code']}")
            print("="*60)
            print("Esperando autenticación...")

            result = app.acquire_token_by_device_flow(flow)

        if "access_token" in result:
            self.access_token = result["access_token"]
            logger.info("✅ Token OAuth2 adquirido exitosamente.")
            # print(f"DEBUG Token: {self.access_token[:10]}...") 
        else:
            raise RuntimeError(f"No se pudo obtener el token: {result.get('error_description')}")

    def _generate_oauth2_string(self, username, token, base64_encode=True):
        """Genera el string XOAUTH2 requerido por el protocolo."""
        # Formato: user={user}^Aauth=Bearer {token}^A^A
        auth_string = f"user={username}\x01auth=Bearer {token}\x01\x01"
        if base64_encode:
            return base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
        return auth_string

    def _get_ssl_context(self):
        return ssl.create_default_context()

    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = self.email_account
        msg['To'] = recipient

        try:
            # Para OAuth con Office365, solemos usar puerto 587 + STARTTLS
            logger.info(f"Conectando a SMTP {self.smtp_host}:{self.smtp_port}...")
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.ehlo()
            server.starttls(context=self._get_ssl_context())
            server.ehlo()

            if self.auth_method == "azure_oauth":
                # Autenticación XOAUTH2 manual
                auth_str = self._generate_oauth2_string(self.email_account, self.access_token)
                code, response = server.docmd("AUTH", "XOAUTH2 " + auth_str)
                if code != 235:
                    raise smtplib.SMTPAuthenticationError(code, response)
            else:
                server.login(self.email_account, self.password)

            server.send_message(msg)
            server.quit()
            logger.info(f"✅ Correo enviado a {recipient}")
            return True
        except Exception as e:
            logger.error(f"❌ Error enviando correo: {e}")
            return False

    def fetch_recent_emails(self, limit: int = 5, folder: str = "INBOX") -> List[Dict]:
        emails = []
        try:
            logger.info(f"Conectando a IMAP {self.imap_host}:{self.imap_port}...")
            
            # Conexión IMAP SSL
            mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port, ssl_context=self._get_ssl_context())

            if self.auth_method == "azure_oauth":
                # Autenticación XOAUTH2 para IMAP
                auth_str = self._generate_oauth2_string(self.email_account, self.access_token, base64_encode=False)
                mail.authenticate('XOAUTH2', lambda x: auth_str)
            else:
                mail.login(self.email_account, self.password)

            mail.select(folder)
            status, messages = mail.search(None, 'ALL')
            
            if status == 'OK':
                mail_ids = messages[0].split()
                recent_ids = mail_ids[-limit:]

                for mail_id in recent_ids:
                    _, msg_data = mail.fetch(mail_id, '(RFC822)')
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            
                            # Decodificar Subject
                            from email.header import decode_header
                            subject = msg.get("subject", "Sin asunto")
                            decoded_list = decode_header(subject)
                            subject_str = ""
                            for content, encoding in decoded_list:
                                if isinstance(content, bytes):
                                    subject_str += content.decode(encoding or "utf-8", errors="replace")
                                else:
                                    subject_str += str(content)

                            emails.append({
                                "id": mail_id.decode(),
                                "sender": msg.get("from"),
                                "subject": subject_str
                            })
            
            mail.close()
            mail.logout()
            return emails

        except Exception as e:
            logger.error(f"❌ Error leyendo correos: {e}")
            return []

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    try:
        # Asegúrate de tener las variables en .env para probar esto
        client = SecureEmailClient()
        print("\n--- Cliente Inicializado ---")
        
        # Prueba de lectura
        msgs = client.fetch_recent_emails(limit=3)
        for m in msgs:
            print(f"- {m['subject']} ({m['sender']})")
            
    except Exception as e:
        print(f"Error: {e}")