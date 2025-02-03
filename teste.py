import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Debug: Print environment variables
username = os.getenv('TRUTHSOCIAL_USERNAME')
password = os.getenv('TRUTHSOCIAL_PASSWORD')

print(f"Loaded credentials:")
print(f"Username: {username}")
print(f"Password: {'*' * len(password) if password else 'Not set'}")

if not username or not password:
    print("Error: Missing required environment variables")
    print("Please check your .env file contains:")
    print("TRUTHSOCIAL_USERNAME=yourusername")
    print("TRUTHSOCIAL_PASSWORD=yourpassword")
    exit(1)

# Main monitoring logic will go here
print("Environment variables loaded successfully!")