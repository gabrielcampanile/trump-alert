import os
import json
import time
import smtplib
import subprocess
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_latest_post(username):
    """Get latest post from a Truth Social user"""
    try:
        result = subprocess.run(
            ["truthbrush", "statuses", username],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout:
            post = json.loads(result.stdout.splitlines()[0])
            return {
                'id': post['id'],
                'content': post['content'].replace('<p>', '').replace('</p>', '')
            }
    except Exception as e:
        print(f"Error fetching post: {e}")
    return None

def send_email_notification(content):
    """Send email notification with post content"""
    try:
        sender = os.getenv('GMAIL_USER')
        password = os.getenv('GMAIL_PASSWORD')
        recipient = os.getenv('NOTIFICATION_EMAIL')

        msg = MIMEText(content)
        msg['Subject'] = 'Nova postagem no Truth Social'
        msg['From'] = sender
        msg['To'] = recipient

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            print("Email notification sent")
    except Exception as e:
        print(f"Error sending email: {e}")

def monitor_account(username):
    """Monitor Truth Social account for new posts"""
    print(f"Starting monitoring for @{username}")
    last_post_id = None

    while True:
        try:
            post = get_latest_post(username)
            if post and post['id'] != last_post_id:
                last_post_id = post['id']
                print(f"New post detected: {post['content']}")
                send_email_notification(post['content'])
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("Monitoring stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    USERNAME = "bielcampanile"
    # USERNAME = "realDonaldTrump"
    monitor_account(USERNAME)