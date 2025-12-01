#!/bin/bash
set -e

echo "🚀 Starting deployment process..."

# Step 1: Check for build errors
echo "🔍 Step 1: Checking for build errors..."
cd ../frontend
npm run build > /dev/null 2>&1 || { echo "❌ Build failed"; exit 1; }
echo "✓ Build check passed"
cd ../iac

# Step 2: Deploy infrastructure
echo "🏗️  Step 2: Deploying infrastructure..."
cdk deploy --require-approval never

# Step 3: Generate amplify outputs
echo "📝 Step 3: Generating amplify_outputs.json..."
python scripts/generate_amplify_config.py

# Step 4: Deploy again with updated config
echo "🔄 Step 4: Deploying with updated config..."
cdk deploy --require-approval never

echo "✅ Deployment completed successfully!"
