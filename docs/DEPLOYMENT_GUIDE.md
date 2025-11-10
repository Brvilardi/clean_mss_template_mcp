# Deployment Guide

Complete guide for deploying the Clean MSS Template microservice to AWS.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [AWS Account Setup](#aws-account-setup)
4. [Deployment Process](#deployment-process)
5. [Environment Configuration](#environment-configuration)
6. [Testing Deployment](#testing-deployment)
7. [Monitoring and Observability](#monitoring-and-observability)
8. [Troubleshooting](#troubleshooting)
9. [Cleanup](#cleanup)

---

## Prerequisites

### Required Tools

1. **Python 3.9+** (tested with Python 3.13)
   ```bash
   python --version  # Should be 3.9 or higher
   ```

2. **Node.js and npm** (for AWS CDK)
   ```bash
   node --version  # v14.x or higher
   npm --version   # v6.x or higher
   ```

3. **AWS CLI**
   ```bash
   aws --version  # v2.x recommended
   ```
   
   Install: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

4. **AWS CDK**
   ```bash
   npm install -g aws-cdk
   cdk --version  # Should be 2.x
   ```

5. **Docker** (for local development)
   ```bash
   docker --version
   docker-compose --version
   ```

### AWS Account Requirements

- Active AWS account
- IAM user with appropriate permissions:
  - Lambda (create, update, delete functions)
  - API Gateway (create, update, delete APIs)
  - DynamoDB (create, update, delete tables)
  - CloudFormation (create, update, delete stacks)
  - IAM (create roles and policies)
  - CloudWatch (logs and metrics)
  - S3 (CDK asset storage)

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd clean_mss_template
```

### 2. Create Python Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
virtualenv -p python3.9 venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install application dependencies
pip install -r requirements-dev.txt

# Install CDK dependencies
cd iac
pip install -r requirements.txt
cd ..
```

### 4. Set Up Local DynamoDB

```bash
cd iac/local
docker-compose up -d
```

This starts DynamoDB Local on `http://localhost:8000`.

### 5. Configure Environment

Create a `.env` file in the project root:

```bash
STAGE=TEST
```

### 6. Run Tests

```bash
pytest
```

Expected output: All tests should pass.

```bash
# Run with coverage
pytest --cov=src --cov-report=html
```

---

## AWS Account Setup

### 1. Configure AWS CLI

```bash
aws configure
```

Enter your credentials:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)
- Default output format: `json`

Verify configuration:
```bash
aws sts get-caller-identity
```

### 2. Set Environment Variables

**Linux/macOS:**
```bash
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=us-east-1
export STACK_NAME=clean-mss-template-dev
```

**Windows (PowerShell):**
```powershell
$env:AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$env:AWS_REGION = "us-east-1"
$env:STACK_NAME = "clean-mss-template-dev"
```

**Windows (Command Prompt):**
```cmd
for /f %i in ('aws sts get-caller-identity --query Account --output text') do set AWS_ACCOUNT_ID=%i
set AWS_REGION=us-east-1
set STACK_NAME=clean-mss-template-dev
```

### 3. Bootstrap CDK (First Time Only)

```bash
cd iac
cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION
```

This creates the necessary S3 bucket and IAM roles for CDK deployments.

---

## Deployment Process

### 1. Navigate to IAC Directory

```bash
cd iac
```

### 2. Synthesize CloudFormation Template

```bash
cdk synth
```

This generates the CloudFormation template. Review the output to ensure everything looks correct.

### 3. Deploy to AWS

**Development Environment:**
```bash
export STACK_NAME=clean-mss-template-dev
cdk deploy
```

**Staging/Homolog Environment:**
```bash
export STACK_NAME=clean-mss-template-homolog
cdk deploy
```

**Production Environment:**
```bash
export STACK_NAME=clean-mss-template-prod
cdk deploy
```

### 4. Confirm Deployment

CDK will show you the changes to be made. Type `y` to confirm.

```
Do you wish to deploy these changes (y/n)? y
```

### 5. Wait for Deployment

Deployment typically takes 3-5 minutes. You'll see progress updates:

```
✨  Synthesis time: 5.2s

clean-mss-template-dev: deploying...
clean-mss-template-dev: creating CloudFormation changeset...

 ✅  clean-mss-template-dev

✨  Deployment time: 180.5s

Outputs:
clean-mss-template-dev.TemplateRestApiEndpoint = https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/

Stack ARN:
arn:aws:cloudformation:us-east-1:123456789012:stack/clean-mss-template-dev/...
```

### 6. Save API Endpoint

Copy the API Gateway endpoint from the outputs:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/
```

---

## Environment Configuration

### Stage Detection

The stack automatically detects the environment based on the stack name:

| Stack Name Contains | Stage | Behavior |
|-------------------|-------|----------|
| `prod` | PROD | Production configuration |
| `homolog` | HOMOLOG | Staging configuration |
| `dev` | DEV | Development configuration |
| Other | TEST | Test configuration (local) |

### Environment Variables

Lambda functions receive these environment variables:

```python
ENVIRONMENT_VARIABLES = {
    "STAGE": "DEV",  # or HOMOLOG, PROD
    "DYNAMO_TABLE_NAME": "user_mss_template-table-dev",
    "DYNAMO_PARTITION_KEY": "PK",
    "DYNAMO_SORT_KEY": "SK",
    "REGION": "us-east-1",
}
```

### Resource Tagging

All resources are automatically tagged:

```python
tags = {
    'project': 'Template',
    'stage': 'DEV',  # or HOMOLOG, PROD
    'stack': 'BACK',
    'owner': 'DevCommunity'
}
```

---

## Testing Deployment

### 1. Test API Endpoint

Replace `<API_ENDPOINT>` with your actual endpoint:

```bash
# Create a user
curl -X POST https://<API_ENDPOINT>/mss-template/create-user \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}'

# Expected response:
# {
#   "user_id": 1,
#   "name": "Test User",
#   "email": "test@example.com",
#   "state": "PENDING",
#   "message": "the user was created successfully"
# }
```

### 2. Get All Users

```bash
curl -X GET https://<API_ENDPOINT>/mss-template/get-all-users
```

### 3. Get Specific User

```bash
curl -X GET "https://<API_ENDPOINT>/mss-template/get-user?user_id=1"
```

### 4. Update User

```bash
curl -X POST https://<API_ENDPOINT>/mss-template/update-user \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "new_name": "Updated Name"}'
```

### 5. Delete User

```bash
curl -X POST https://<API_ENDPOINT>/mss-template/delete-user \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

---

## Monitoring and Observability

### CloudWatch Logs

View Lambda function logs:

```bash
# List log groups
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/clean-mss-template

# Tail logs for a specific function
aws logs tail /aws/lambda/clean-mss-template-dev-create-user --follow
```

### CloudWatch Metrics

Monitor key metrics:
- Lambda invocations
- Lambda errors
- Lambda duration
- API Gateway requests
- API Gateway 4xx/5xx errors
- DynamoDB read/write capacity

Access metrics in AWS Console:
1. Navigate to CloudWatch
2. Select "Metrics"
3. Choose "Lambda" or "API Gateway" or "DynamoDB"

### X-Ray Tracing

View distributed traces:

1. Navigate to AWS X-Ray console
2. Select "Service map" to see architecture
3. Select "Traces" to see individual requests
4. Filter by error status or latency

### Custom Dashboards

Create a CloudWatch dashboard:

```bash
aws cloudwatch put-dashboard \
  --dashboard-name clean-mss-template-dev \
  --dashboard-body file://dashboard.json
```

---

## CI/CD Integration

### GitHub Actions

The project includes CI/CD workflows in `.github/workflows/`:

**CI.yml** - Continuous Integration:
- Runs on pull requests
- Executes tests
- Checks code coverage

**CD.yml** - Continuous Deployment:
- Runs on push to main branch
- Deploys to AWS automatically
- Updates infrastructure

**CREATE_PR.yml** - Pull Request Automation:
- Automates PR creation
- Branch management

### Setting Up GitHub Secrets

Add these secrets to your GitHub repository:

1. `AWS_ACCESS_KEY_ID`
2. `AWS_SECRET_ACCESS_KEY`
3. `AWS_REGION`
4. `AWS_ACCOUNT_ID`

Navigate to: Repository Settings → Secrets and variables → Actions → New repository secret

---

## Updating Deployment

### Update Application Code

1. Make changes to source code
2. Run tests locally: `pytest`
3. Commit changes
4. Deploy update:

```bash
cd iac
cdk deploy
```

CDK will detect changes and update only affected resources.

### Update Infrastructure

1. Modify CDK code in `iac/iac/`
2. Synthesize to preview changes:

```bash
cdk synth
```

3. Review the diff:

```bash
cdk diff
```

4. Deploy changes:

```bash
cdk deploy
```

### Rollback Deployment

If something goes wrong:

```bash
# List stack events
aws cloudformation describe-stack-events \
  --stack-name clean-mss-template-dev \
  --max-items 20

# Rollback to previous version
aws cloudformation rollback-stack \
  --stack-name clean-mss-template-dev
```

---

## Multi-Environment Strategy

### Development Environment

```bash
export STACK_NAME=clean-mss-template-dev
cdk deploy
```

- Used for active development
- Frequent deployments
- Lower resource limits
- Cost-optimized

### Staging/Homolog Environment

```bash
export STACK_NAME=clean-mss-template-homolog
cdk deploy
```

- Pre-production testing
- Mirrors production configuration
- Integration testing
- Performance testing

### Production Environment

```bash
export STACK_NAME=clean-mss-template-prod
cdk deploy
```

- Live user traffic
- High availability
- Enhanced monitoring
- Backup and disaster recovery

### Best Practices

1. **Never deploy directly to production** - Always test in dev/homolog first
2. **Use separate AWS accounts** for production isolation
3. **Implement approval gates** for production deployments
4. **Tag all resources** with environment information
5. **Monitor costs** per environment
6. **Automate deployments** through CI/CD pipelines

---

## Troubleshooting

### Common Issues

#### 1. CDK Bootstrap Error

**Error**: `Need to perform AWS calls for account XXX, but no credentials configured`

**Solution**:
```bash
aws configure
cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION
```

#### 2. Insufficient Permissions

**Error**: `User is not authorized to perform: lambda:CreateFunction`

**Solution**: Ensure your IAM user has the required permissions. Attach these policies:
- AWSLambda_FullAccess
- AmazonAPIGatewayAdministrator
- AmazonDynamoDBFullAccess
- CloudFormationFullAccess
- IAMFullAccess (or specific role creation permissions)

#### 3. Stack Already Exists

**Error**: `Stack [name] already exists`

**Solution**:
```bash
# Update existing stack
cdk deploy

# Or delete and recreate
cdk destroy
cdk deploy
```

#### 4. Python 3.13 Compatibility Issues

**Error**: `ModuleNotFoundError: No module named 'cgi'`

**Solution**: Update boto3 to support Python 3.13:
```bash
pip install --upgrade boto3
```

**Alternative**: Use Python 3.12 or earlier if you need to maintain specific boto3 versions.

#### 4. Lambda Layer Too Large

**Error**: `Unzipped size must be smaller than 262144000 bytes`

**Solution**: The `adjust_layer_directory.py` script should handle this. If issues persist:
```bash
cd iac
python adjust_layer_directory.py
```

#### 5. DynamoDB Table Already Exists

**Error**: `Table already exists`

**Solution**: Change the table name in the stack or delete the existing table:
```bash
aws dynamodb delete-table --table-name user_mss_template-table-dev
```

#### 6. API Gateway 502 Bad Gateway

**Cause**: Lambda function error

**Solution**:
1. Check CloudWatch Logs:
```bash
aws logs tail /aws/lambda/clean-mss-template-dev-create-user --follow
```
2. Look for Python exceptions
3. Fix code and redeploy

#### 7. CORS Errors

**Cause**: Missing CORS headers

**Solution**: The template includes CORS configuration. Verify in `iac/iac/template_stack.py`:
```python
default_cors_preflight_options={
    "allow_origins": Cors.ALL_ORIGINS,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["*"]
}
```

---

## Cleanup

### Delete Stack

To remove all AWS resources:

```bash
cd iac
cdk destroy
```

Confirm deletion when prompted.

### Manual Cleanup

If `cdk destroy` fails, manually delete:

1. **CloudFormation Stack**:
```bash
aws cloudformation delete-stack --stack-name clean-mss-template-dev
```

2. **DynamoDB Table** (if not deleted):
```bash
aws dynamodb delete-table --table-name user_mss_template-table-dev
```

3. **CloudWatch Log Groups**:
```bash
aws logs delete-log-group --log-group-name /aws/lambda/clean-mss-template-dev-create-user
aws logs delete-log-group --log-group-name /aws/lambda/clean-mss-template-dev-get-user
# ... repeat for all functions
```

4. **S3 CDK Assets** (optional):
```bash
aws s3 rb s3://cdk-hnb659fds-assets-$AWS_ACCOUNT_ID-$AWS_REGION --force
```

### Verify Cleanup

```bash
# Check for remaining stacks
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE

# Check for Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `clean-mss-template`)].FunctionName'

# Check for DynamoDB tables
aws dynamodb list-tables --query 'TableNames[?contains(@, `user_mss_template`)]'
```

---

## Cost Estimation

### AWS Free Tier (First 12 Months)

- **Lambda**: 1M requests/month, 400,000 GB-seconds compute
- **API Gateway**: 1M API calls/month
- **DynamoDB**: 25 GB storage, 25 read/write capacity units

### Estimated Monthly Costs (Beyond Free Tier)

**Low Traffic** (10,000 requests/month):
- Lambda: ~$0.20
- API Gateway: ~$0.04
- DynamoDB: ~$1.25
- **Total**: ~$1.50/month

**Medium Traffic** (100,000 requests/month):
- Lambda: ~$2.00
- API Gateway: ~$0.35
- DynamoDB: ~$2.50
- **Total**: ~$5.00/month

**High Traffic** (1,000,000 requests/month):
- Lambda: ~$20.00
- API Gateway: ~$3.50
- DynamoDB: ~$12.50
- **Total**: ~$36.00/month

*Note: Costs vary by region and usage patterns. Use AWS Cost Calculator for accurate estimates.*

---

## Security Best Practices

1. **Use IAM roles** instead of hardcoded credentials
2. **Enable CloudTrail** for audit logging
3. **Encrypt data at rest** (DynamoDB encryption enabled by default)
4. **Use VPC** for Lambda functions (if accessing private resources)
5. **Implement API authentication** (Cognito, IAM, or custom authorizers)
6. **Enable AWS WAF** for API Gateway protection
7. **Rotate credentials** regularly
8. **Use AWS Secrets Manager** for sensitive configuration
9. **Enable MFA** for AWS account access
10. **Review IAM policies** regularly

---

## Next Steps

After successful deployment:

1. **Set up monitoring alerts** in CloudWatch
2. **Configure backup strategy** for DynamoDB
3. **Implement authentication** for API endpoints
4. **Add custom domain** to API Gateway
5. **Set up SSL certificate** with AWS Certificate Manager
6. **Configure WAF rules** for security
7. **Implement rate limiting** with API Gateway usage plans
8. **Add more features** following the Clean Architecture pattern
9. **Set up automated testing** in CI/CD pipeline
10. **Document API** with OpenAPI/Swagger

---

## Support and Resources

- **AWS Documentation**: https://docs.aws.amazon.com/
- **AWS CDK Documentation**: https://docs.aws.amazon.com/cdk/
- **Clean Architecture**: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- **Dev. Community Mauá**: https://www.instagram.com/devcommunitymaua/

---

## Deployment Checklist

- [ ] Python 3.9+ installed
- [ ] AWS CLI configured
- [ ] AWS CDK installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Tests passing locally
- [ ] AWS account configured
- [ ] Environment variables set
- [ ] CDK bootstrapped
- [ ] Stack deployed successfully
- [ ] API endpoint tested
- [ ] CloudWatch logs verified
- [ ] X-Ray tracing enabled
- [ ] Monitoring dashboard created
- [ ] Documentation updated
- [ ] Team notified of deployment
