#!/usr/bin/env python3
"""
Test script for /sessions endpoint with Cognito authentication.

This script authenticates with Cognito using AWS CLI and tests the sessions endpoint.
"""

import json
import subprocess
import sys
import requests
from getpass import getpass


# Configuration from CDK outputs
USER_POOL_ID = "[REPLACE WITH YORS]"
CLIENT_ID = "[REPLACE WITH YORS]"
SESSIONS_API_URL = "[REPLACE WITH YORS]"
REGION = "[REPLACE WITH YORS]"

# Hard-coded credentials for testing
TEST_EMAIL = "[REPLACE WITH YORS]"
TEST_PASSWORD = "[REPLACE WITH YORS]"
TEST_SESSION_ID = "[REPLACE WITH YORS]"


def authenticate(email: str, password: str) -> dict:
    """
    Authenticate with Cognito and get tokens.
    
    Args:
        email: User email
        password: User password
        
    Returns:
        Dictionary with IdToken, AccessToken, RefreshToken
    """
    print("\n🔐 Authenticating with Cognito...")
    
    cmd = [
        "aws", "cognito-idp", "initiate-auth",
        "--auth-flow", "USER_PASSWORD_AUTH",
        "--client-id", CLIENT_ID,
        "--auth-parameters", f"USERNAME={email},PASSWORD={password}",
        "--region", REGION
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        response = json.loads(result.stdout)
        
        if "AuthenticationResult" in response:
            print("✅ Authentication successful")
            return response["AuthenticationResult"]
        else:
            print("❌ Authentication failed - no AuthenticationResult in response")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Authentication failed: {e.stderr}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse response: {e}")
        sys.exit(1)


def test_sessions_endpoint(id_token: str):
    """
    Test the /sessions endpoint with authentication (no session_id).
    
    Args:
        id_token: Cognito ID token
    """
    print("\n📡 TEST 1: /sessions endpoint WITHOUT session_id parameter...")
    
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json"
    }

    
    try:
        print(f"   URL: {SESSIONS_API_URL}")
        response = requests.get(SESSIONS_API_URL, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Request successful")
            data = response.json()
            print(f"\n📊 Response:")
            print(json.dumps(data, indent=2))
            print(f"\n✨ Total sessions: {data.get('count', 0)}")
            
        elif response.status_code == 401:
            print("❌ Unauthorized - Token may be invalid")
            print(response.text)
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")


def test_session_events(id_token: str, session_id: str):
    """
    Test the /sessions endpoint with session_id parameter.
    
    Args:
        id_token: Cognito ID token
        session_id: Session ID to fetch events for
    """
    print(f"\n📡 TEST 2: /sessions endpoint WITH session_id={session_id}...")
    
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json"
    }

    
    try:
        url = f"{SESSIONS_API_URL}?session_id={session_id}"
        print(f"   URL: {url}")
        response = requests.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Request successful")
            data = response.json()
            print(f"\n📊 Response:")
            print(json.dumps(data, indent=2))
            print(f"\n✨ Total events: {data.get('event_count', 0)}")
            
        elif response.status_code == 401:
            print("❌ Unauthorized - Token may be invalid")
            print(response.text)
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")


def test_without_auth():
    """Test the endpoint without authentication (should fail)."""
    print("\n🚫 Testing /sessions endpoint without authentication...")
    
    try:
        response = requests.get(SESSIONS_API_URL)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected unauthorized request")
        else:
            print(f"⚠️  Expected 401 but got {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")


def main():
    """Main test function."""
    print("=" * 60)
    print("Testing /sessions endpoint with Cognito authentication")
    print("=" * 60)
    
    # Use hard-coded credentials
    email = TEST_EMAIL
    password = TEST_PASSWORD
    print(f"\n📧 Using test email: {email}")
    print(f"🔑 Using test password: {'*' * len(password)}")
    print(f"🆔 Test session ID: {TEST_SESSION_ID}")
    
    # Authenticate
    auth_result = authenticate(email, password)
    id_token = auth_result["IdToken"]
    print(f"🔑 ID Token: {id_token}")
    
    # # Test with authentication (no session_id)
    # test_sessions_endpoint(id_token)
    
    # Test with authentication and session_id
    test_session_events(id_token, TEST_SESSION_ID)
    
    # # Test without authentication
    # test_without_auth()
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
