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


def generate_amplify_config(
    outputs: dict = None, 
    region: str = None, 
    cloudfront_url: str = None,
    user_pool_id: str = None,
    user_pool_client_id: str = None,
    identity_pool_id: str = None,
    user_pool_domain: str = None,
    api_gateway_url: str = None
) -> dict:
    """
    Generate amplify_outputs.json from stack outputs or direct parameters.
    
    Can be called in two modes:
    1. With outputs dict (reads from CloudFormation stack)
    2. With direct parameters (for CDK synthesis-time generation)
    """
    
    # If direct parameters provided, use them
    if all([user_pool_id, user_pool_client_id, identity_pool_id, user_pool_domain, api_gateway_url, region]):
        pass  # Use provided parameters
    # Otherwise extract from outputs dict
    elif outputs:
        user_pool_id = find_output_by_prefix(outputs, 'CognitoStackUserPoolId') or outputs.get('UserPoolId')
        user_pool_client_id = find_output_by_prefix(outputs, 'CognitoStackUserPoolClientId') or outputs.get('UserPoolClientId')
        identity_pool_id = find_output_by_prefix(outputs, 'CognitoStackIdentityPoolId') or outputs.get('IdentityPoolId')
        user_pool_domain = find_output_by_prefix(outputs, 'CognitoStackUserPoolDomain') or outputs.get('UserPoolDomain')
        api_gateway_url = outputs.get('ApiGatewayBaseUrl')
    else:
        raise ValueError("Must provide either outputs dict or all direct parameters")
    
    if not all([user_pool_id, user_pool_client_id, identity_pool_id, user_pool_domain, api_gateway_url]):
        missing = [k for k, v in {
            'UserPoolId': user_pool_id,
            'UserPoolClientId': user_pool_client_id,
            'IdentityPoolId': identity_pool_id,
            'UserPoolDomain': user_pool_domain,
            'ApiGatewayBaseUrl': api_gateway_url
        }.items() if not v]
        raise ValueError(f"Missing required outputs: {', '.join(missing)}")
    
    # Determine redirect URLs based on CloudFront URL
    # Use CloudFront URL for production, localhost for local development
    if cloudfront_url:
        redirect_sign_in = f"{cloudfront_url}/"
        redirect_sign_out = f"{cloudfront_url}/"
    else:
        redirect_sign_in = "http://localhost:5173/"
        redirect_sign_out = "http://localhost:5173/"
    
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
                "redirect_sign_in": redirect_sign_in,
                "redirect_sign_out": redirect_sign_out,
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
        help='CloudFormation stack name (required for stack mode)'
    )
    parser.add_argument(
        '--region',
        help='AWS region (required)'
    )
    parser.add_argument(
        '--output',
        default='../../frontend/amplify_outputs.json',
        help='Output file path (default: ../../frontend/amplify_outputs.json)'
    )
    parser.add_argument(
        '--cloudfront-url',
        help='CloudFront distribution URL for OAuth redirect URLs (e.g., https://d123456.cloudfront.net)'
    )
    # Direct parameter mode (for CDK synthesis)
    parser.add_argument('--user-pool-id', help='Cognito User Pool ID')
    parser.add_argument('--user-pool-client-id', help='Cognito User Pool Client ID')
    parser.add_argument('--identity-pool-id', help='Cognito Identity Pool ID')
    parser.add_argument('--user-pool-domain', help='Cognito User Pool Domain')
    parser.add_argument('--api-gateway-url', help='API Gateway base URL')
    
    args = parser.parse_args()
    
    # Check if using direct parameter mode
    direct_params = all([
        args.user_pool_id,
        args.user_pool_client_id,
        args.identity_pool_id,
        args.user_pool_domain,
        args.api_gateway_url,
        args.region
    ])
    
    if direct_params:
        # Direct parameter mode (CDK synthesis)
        print("Using direct parameters mode...")
        cloudfront_url = args.cloudfront_url
        config = generate_amplify_config(
            region=args.region,
            cloudfront_url=cloudfront_url,
            user_pool_id=args.user_pool_id,
            user_pool_client_id=args.user_pool_client_id,
            identity_pool_id=args.identity_pool_id,
            user_pool_domain=args.user_pool_domain,
            api_gateway_url=args.api_gateway_url
        )
    else:
        # CloudFormation stack mode
        if not args.stack_name:
            raise ValueError("--stack-name is required when not using direct parameters")
        
        print(f"Fetching outputs from stack: {args.stack_name}")
        outputs = get_stack_outputs(args.stack_name, args.region)
        
        # If CloudFront URL not provided via CLI, try to get it from stack outputs
        cloudfront_url = args.cloudfront_url
        if not cloudfront_url:
            cloudfront_url = find_output_by_prefix(outputs, 'FrontendStackCloudFrontDistributionURL')
        
        print("Generating amplify_outputs.json...")
        if cloudfront_url:
            print(f"Using CloudFront URL for OAuth redirects: {cloudfront_url}")
        else:
            print("Using localhost URLs for OAuth redirects (local development)")
        
        config = generate_amplify_config(outputs, args.region, cloudfront_url)
    
    # Write to file
    # Resolve output path relative to project root, not script location
    if args.output.startswith('../'):
        # Relative path from script dir - resolve to absolute
        output_path = (Path(__file__).parent / args.output).resolve()
    else:
        # Absolute or simple path
        output_path = Path(args.output).resolve()
    
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
