#!/usr/bin/env python3
"""
Script to generate amplify_outputs.json from CDK outputs.

This script reads the CloudFormation stack outputs and generates
the amplify_outputs.json configuration file for the frontend.

Usage:
    python generate_amplify_config.py --stack-name <stack-name> --region <region>
"""

import json
import argparse
import boto3
from pathlib import Path


def get_stack_outputs(stack_name: str, region: str) -> dict:
    """Get CloudFormation stack outputs."""
    cfn = boto3.client('cloudformation', region_name=region)
    
    try:
        response = cfn.describe_stacks(StackName=stack_name)
        stack = response['Stacks'][0]
        outputs = {output['OutputKey']: output['OutputValue'] 
                  for output in stack.get('Outputs', [])}
        return outputs
    except Exception as e:
        print(f"Error getting stack outputs: {e}")
        raise


def find_output_by_prefix(outputs: dict, prefix: str) -> str:
    """Find output value by key prefix (handles CDK-generated suffixes)."""
    for key, value in outputs.items():
        if key.startswith(prefix):
            return value
    return None


def generate_amplify_config(outputs: dict, region: str) -> dict:
    """Generate amplify_outputs.json from stack outputs."""
    
    # Extract values from outputs (handle CDK-generated key suffixes)
    user_pool_id = find_output_by_prefix(outputs, 'CognitoStackUserPoolId') or outputs.get('UserPoolId')
    user_pool_client_id = find_output_by_prefix(outputs, 'CognitoStackUserPoolClientId') or outputs.get('UserPoolClientId')
    identity_pool_id = find_output_by_prefix(outputs, 'CognitoStackIdentityPoolId') or outputs.get('IdentityPoolId')
    user_pool_domain = find_output_by_prefix(outputs, 'CognitoStackUserPoolDomain') or outputs.get('UserPoolDomain')
    api_gateway_url = outputs.get('ApiGatewayBaseUrl')
    
    if not all([user_pool_id, user_pool_client_id, identity_pool_id, user_pool_domain, api_gateway_url]):
        missing = [k for k, v in {
            'UserPoolId': user_pool_id,
            'UserPoolClientId': user_pool_client_id,
            'IdentityPoolId': identity_pool_id,
            'UserPoolDomain': user_pool_domain,
            'ApiGatewayBaseUrl': api_gateway_url
        }.items() if not v]
        raise ValueError(f"Missing required outputs: {', '.join(missing)}")
    
    config = {
        "version": "1",
        "auth": {
            "user_pool_id": user_pool_id,
            "aws_region": region,
            "user_pool_client_id": user_pool_client_id,
            "identity_pool_id": identity_pool_id,
            "oauth": {
                "domain": user_pool_domain,
                "scope": [
                    "email",
                    "openid",
                    "profile"
                ],
                "redirect_sign_in": "http://localhost:5173/",
                "redirect_sign_out": "http://localhost:5173/",
                "response_type": "code"
            },
            "password_policy": {
                "min_length": 8,
                "require_lowercase": True,
                "require_uppercase": True,
                "require_numbers": True,
                "require_symbols": True
            },
            "username_attributes": [
                "email"
            ],
            "user_verification_types": [
                "email"
            ],
            "mfa_configuration": "OFF",
            "mfa_types": [],
            "standard_required_attributes": [
                "email"
            ]
        },
        "data": {
            "aws_region": region
        },
        "custom": {
            "api": {
                "StrandsAgentAPI": {
                    "endpoint": f"{api_gateway_url}/agent",
                    "region": region
                }
            }
        }
    }
    
    return config


def main():
    parser = argparse.ArgumentParser(
        description='Generate amplify_outputs.json from CDK stack outputs'
    )
    parser.add_argument(
        '--stack-name',
        required=True,
        help='CloudFormation stack name'
    )
    parser.add_argument(
        '--region',
        required=True,
        help='AWS region'
    )
    parser.add_argument(
        '--output',
        default='../frontend/amplify_outputs.json',
        help='Output file path (default: ../frontend/amplify_outputs.json)'
    )
    
    args = parser.parse_args()
    
    print(f"Fetching outputs from stack: {args.stack_name}")
    outputs = get_stack_outputs(args.stack_name, args.region)
    
    print("Generating amplify_outputs.json...")
    config = generate_amplify_config(outputs, args.region)
    
    # Write to file
    output_path = Path(__file__).parent / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Successfully generated {output_path}")
    print("\nConfiguration:")
    print(f"  User Pool ID: {config['auth']['user_pool_id']}")
    print(f"  Client ID: {config['auth']['user_pool_client_id']}")
    print(f"  Identity Pool ID: {config['auth']['identity_pool_id']}")
    print(f"  API Endpoint: {config['custom']['api']['StrandsAgentAPI']['endpoint']}")


if __name__ == '__main__':
    main()
