#!/usr/bin/env python3
"""
Test script for directly calling AgentCore Memory API using boto3.

This script tests the bedrock-agentcore list_events API to verify
that events can be retrieved for a specific session.

NOTE: The actor_id should match the Cognito user's 'sub' or 'cognito:username' claim.
When testing the agent endpoint, the actor_id is automatically extracted from the
Cognito JWT token by the API Gateway authorizer.
"""

import boto3
import json
from pprint import pprint

# Configuration
MEMORY_ID = "[REPLACE WITH YORS]"
# IMPORTANT: This actor_id should match the Cognito user's 'sub' or 'cognito:username'
# The agent endpoint will extract this automatically from the JWT token
ACTOR_ID = "[REPLACE WITH YORS]"
SESSION_ID = "[REPLACE WITH YORS]"
REGION = "[REPLACE WITH YORS]"


def test_list_events():
    """Test listing events from AgentCore Memory."""
    print("=" * 70)
    print("Testing AgentCore Memory list_events API")
    print("=" * 70)
    
    print(f"\n📋 Configuration:")
    print(f"   Memory ID:  {MEMORY_ID}")
    print(f"   Actor ID:   {ACTOR_ID}")
    print(f"   Session ID: {SESSION_ID}")
    print(f"   Region:     {REGION}")
    
    # Create boto3 client
    print(f"\n🔧 Creating bedrock-agentcore client...")
    client = boto3.client("bedrock-agentcore", region_name=REGION)
    
    try:
        print(f"\n📡 Calling list_events API...")
        response = client.list_events(
            memoryId=MEMORY_ID,
            actorId=ACTOR_ID,
            sessionId=SESSION_ID,
            includePayloads=True,
            maxResults=100
        )
        
        print(f"\n✅ API call successful!")
        
        # Extract events
        events = response.get("events", [])
        next_token = response.get("nextToken")
        
        print(f"\n📊 Results:")
        print(f"   Events count: {len(events)}")
        print(f"   Has more pages: {'Yes' if next_token else 'No'}")
        
        if events:
            print(f"\n📝 Events:")
            # for i, event in enumerate(events, 1):
            #     print(f"\n   Event {i}:")
            #     print(f"      Event ID:   {event.get('eventId', 'N/A')}")
            #     print(f"      Event Type: {event.get('eventType', 'N/A')}")
            #     print(f"      Timestamp:  {event.get('timestamp', 'N/A')}")
                
            #     # Show payload if available
            #     payload = event.get("payload")
            #     if payload:
            #         print(f"      Payload:")
            #         print(f"         {json.dumps(payload, indent=10)[:200]}...")
        else:
            print(f"\n   ℹ️  No events found for this session")
            print(f"   This could mean:")
            print(f"      - The session exists but has no events yet")
            print(f"      - The session ID is incorrect")
            print(f"      - The actor ID doesn't match the session owner")
        
        print(f"\n📄 Full Response:")
        # pprint(response, width=100)
        
    except client.exceptions.ResourceNotFoundException as e:
        print(f"\n❌ Resource not found:")
        print(f"   {str(e)}")
        print(f"\n   Possible causes:")
        print(f"      - Memory ID is incorrect")
        print(f"      - Session ID doesn't exist")
        print(f"      - Actor ID doesn't match")
        
    except client.exceptions.AccessDeniedException as e:
        print(f"\n❌ Access denied:")
        print(f"   {str(e)}")
        print(f"\n   Check IAM permissions for:")
        print(f"      - bedrock-agentcore:ListEvents")
        print(f"      - bedrock-agentcore:GetEvent")
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}")
        print(f"   {str(e)}")
        import traceback
        print(f"\n   Traceback:")
        print(traceback.format_exc())
    
    print(f"\n" + "=" * 70)
    print("Test completed")
    print("=" * 70)


if __name__ == "__main__":
    test_list_events()
