#!/bin/bash

# Script to manually invalidate CloudFront cache after deployment
# Usage: ./invalidate_cloudfront.sh [stack-name]

STACK_NAME=${1:-"CleanMssTemplateStack"}

echo "Getting CloudFront Distribution ID for stack: $STACK_NAME"

# Get the distribution ID from CloudFormation outputs
DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" \
  --output text)

if [ -z "$DISTRIBUTION_ID" ]; then
  echo "Error: Could not find CloudFront Distribution ID"
  echo 