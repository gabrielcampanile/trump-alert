import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def test_email():
    try:
        sender = os.getenv('GMAIL_USER')
        password = os.getenv('GMAIL_PASSWORD')
        recipient = os.getenv('NOTIFICATION_EMAIL')

        msg = MIMEText("Test email from Truth Social Monitor")
        msg['Subject'] = 'Test Email'
        msg['From'] = sender
        msg['To'] = recipient

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            print("Test email sent successfully!")
    except Exception as e:
        print(f"Email error: {e}")

if __name__ == "__main__":
    test_email()