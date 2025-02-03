import os
import json
import time
import smtplib
import subprocess
from datetime import datetime
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables and configuration
load_dotenv()
CHECK_INTERVAL = 15  # seconds
MAX_RETRIES = 3
BACKOFF_TIME = 30

def get_recipients():
    """Get list of email recipients"""
    recipients = os.getenv('NOTIFICATION_EMAILS', '')
    return [email.strip() for email in recipients.split(',') if email.strip()]

def get_latest_post(username):
    """Fetch latest post or retruth from Truth Social"""
    try:
        result = subprocess.run(
            ["truthbrush", "statuses", username],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout:
            post = json.loads(result.stdout.splitlines()[0])
            created_at = datetime.fromisoformat(post['created_at'].replace('Z', '+00:00'))
            local_time = created_at.astimezone().strftime('%d/%m/%Y %H:%M:%S')
            
            # Check if it's a retruth
            if post.get('reblog'):
                original_post = post['reblog']
                return {
                    'id': post['id'],
                    'content': original_post['content'].replace('<p>', '').replace('</p>', ''),
                    'username': username,
                    'timestamp': local_time,
                    'url': original_post['url'],
                    'is_retruth': True,
                    'original_author': original_post['account']['username']
                }
            
            return {
                'id': post['id'],
                'content': post['content'].replace('<p>', '').replace('</p>', ''),
                'username': username,
                'timestamp': local_time,
                'url': post['url'],
                'is_retruth': False,
                'original_author': username
            }
    except Exception as e:
        print(f"Error fetching post: {e}")
    return None

def send_email_notification(post_data):
    """Send email notification with retruth support"""
    sender = os.getenv('GMAIL_USER')
    password = os.getenv('GMAIL_PASSWORD')
    recipients = get_recipients()

    message = f"""
Nova {'ReTruth' if post_data['is_retruth'] else 'postagem'} no Truth Social!
----------------------------
{'Post original de: @' + post_data['original_author'] if post_data['is_retruth'] else 'Autor: @' + post_data['username']}
Data/Hora: {post_data['timestamp']}
Conteúdo: {post_data['content']}
Link: {post_data['url']}
"""

    try:
        msg = MIMEText(message)
        msg['Subject'] = f"{'ReTruth' if post_data['is_retruth'] else 'Nova postagem'} de @{post_data['username']}"
        msg['From'] = sender

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            
            for recipient in recipients:
                try:
                    msg['To'] = recipient
                    server.send_message(msg)
                    print(f"Notification sent to {recipient}")
                except Exception as e:
                    print(f"Failed to send to {recipient}: {e}")

    except Exception as e:
        print(f"Email error: {e}")

def monitor_account(username):
    """Monitor Truth Social account for new posts and retruth"""
    print(f"Starting monitoring for @{username}")
    last_post_id = None
    error_count = 0

    while True:
        try:
            post = get_latest_post(username)
            if post and post['id'] != last_post_id:
                last_post_id = post['id']
                print(f"New {'retruth' if post['is_retruth'] else 'post'} detected from @{username}")
                print(f"Content: {post['content']}")
                print(f"Time: {post['timestamp']}")
                send_email_notification(post)
                error_count = 0
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            break
            
        except Exception as e:
            error_count += 1
            wait_time = BACKOFF_TIME * error_count
            print(f"Error: {e}")
            print(f"Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
            
            if error_count >= MAX_RETRIES:
                print("Max retries reached, resetting error count")
                error_count = 0

if __name__ == "__main__":
    # USERNAME = "bielcampanile"
    USERNAME = "realDonaldTrump"
    monitor_account(USERNAME)