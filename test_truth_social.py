import os
import json
import time
import subprocess
from dotenv import load_dotenv

def test_auth(debug=True):
    """Test Truth Social authentication with detailed logging"""
    try:
        if debug:
            print("\nTesting authentication...")
            print(f"Using username: {os.getenv('TRUTHSOCIAL_USERNAME')}")
        
        # Test using tags command which requires authentication
        test_result = subprocess.run(
            ["truthbrush", "tags"],
            capture_output=True,
            text=True
        )
        
        if debug:
            print(f"\nAuth response:")
            print(f"Return code: {test_result.returncode}")
            print(f"Error output: {test_result.stderr if test_result.stderr else 'None'}")
        
        if test_result.returncode == 0:
            print("✓ Authentication successful")
            return True
            
        print(f"✗ Authentication failed: {test_result.stderr}")
        return False
        
    except Exception as e:
        print(f"✗ Authentication error: {str(e)}")
        return False

def test_truth_connection(username, max_retries=3):
    """Test Truth Social connection with retry logic"""
    print("\nTesting Truth Social setup...")
    
    # Load and verify credentials
    load_dotenv()
    ts_user = os.getenv('TRUTHSOCIAL_USERNAME')
    ts_pass = os.getenv('TRUTHSOCIAL_PASSWORD')
    
    if not ts_user or not ts_pass:
        print("✗ Error: Missing Truth Social credentials in .env")
        return False
        
    print(f"✓ Credentials found in .env")
    
    # Test authentication
    if not test_auth(debug=True):
        return False
        
    # Test API access
    print(f"\nTesting API access for @{username}...")
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["truthbrush", "statuses", username],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout:
                post = json.loads(result.stdout.splitlines()[0])
                print("✓ API access successful")
                print("\nLatest post details:")
                print(f"Content: {post['content'].replace('<p>', '').replace('</p>', '')}")
                return True
                
            if "429" in result.stderr:
                wait_time = 60 * (attempt + 1)
                print(f"Rate limit hit, waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
                
            print(f"✗ API error: {result.stderr}")
            return False
            
        except Exception as e:
            print(f"✗ Test failed: {str(e)}")
            return False
    
    print("✗ Max retries reached")
    return False

if __name__ == "__main__":
    USERNAME = "bielcampanile"
    test_truth_connection(USERNAME)