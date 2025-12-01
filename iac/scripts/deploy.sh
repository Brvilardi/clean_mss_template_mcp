#!/bin/bash
set -e

# Deployment script that ensures amplify_outputs.json is up-to-date before building

echo "🚀 Starting deployment process..."

# Get stack name and region from environment or use defaults
STACK_NAME=${STACK_NAME:-"clean-mss-template"}
AWS_REGION=${AWS_REGION:-"us-west-2"}

echo "📋 Configuration:"
echo "  Stack: $STACK_NAME"
echo "  Region: $AWS_REGION"

# Step 1: Generate amplify_outputs.json from deployed stack
echo ""
echo "📝 Step 1: Generating amplify_outputs.json..."
python scripts/generate_amplify_config.py \
  --stack-name "$STACK_NAME" \
  --region "$AWS_REGION"

if [ $? -ne 0 ]; then
  echo "❌ Failed to generate amplify_outputs.json"
  exit 1
fi

# Step 2: Deploy with CDK (which will build frontend with correct config)
echo ""
echo "🏗️  Step 2: Deploying with CDK..."
cdk deploy --require-approval never

if [ $? -ne 0 ]; then
  echo "❌ CDK deployment failed"
  exit 1
fi

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Frontend URL: https://$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --region "$AWS_REGION" \
  --query 'Stacks[0].Outputs[?OutputKey==`FrontendStackCloudFrontDomainName5912B3C2`].OutputValue' \
  --output text)"
