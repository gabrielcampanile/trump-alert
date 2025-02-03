import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Configuration
load_dotenv()
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587

def test_email():
    try:
        # Get credentials
        sender = os.getenv('OUTLOOK_USER')
        password = os.getenv('OUTLOOK_PASSWORD')
        recipients = [email.strip() for email in os.getenv('NOTIFICATION_EMAILS', '').split(',')]

        # Create message
        message = "Este é um email de teste do monitor Truth Social."
        msg = MIMEText(message)
        msg['Subject'] = 'Teste de Envio - Truth Social Monitor'
        msg['From'] = sender

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(sender, password)
            
            for recipient in recipients:
                try:
                    msg['To'] = recipient
                    server.send_message(msg)
                    print(f"✓ Teste enviado para {recipient}")
                except Exception as e:
                    print(f"✗ Falha no envio para {recipient}: {e}")

    except Exception as e:
        print(f"Erro no teste: {e}")

if __name__ == "__main__":
    test_email()