# Cognito Authentication Setup

This document describes the AWS Cognito configuration for the re:Invent Planner frontend application.

## Overview

The application uses AWS Cognito for user authentication with custom attributes to store company information. The setup includes:

- **User Pool**: Manages user accounts and authentication
- **User Pool Client**: Configured for the web application (SPA)
- **Identity Pool**: Provides AWS credentials for authenticated users
- **Custom Attributes**: Stores company name and website

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React SPA)                     │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              AWS Amplify Auth                           │ │
│  │  - Sign Up / Sign In                                   │ │
│  │  - Token Management                                    │ │
│  │  - Session Persistence                                 │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    AWS Cognito User Pool                     │
│                                                              │
│  - Email-based authentication                               │
│  - Custom attributes (company_name, company_website)        │
│  - Password policy enforcement                              │
│  - Email verification                                       │
│  - OAuth 2.0 / OIDC support                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  AWS Cognito Identity Pool                   │
│                                                              │
│  - Provides temporary AWS credentials                       │
│  - Enables API Gateway authentication                       │
└─────────────────────────────────────────────────────────────┘
```

## User Pool Configuration

### Authentication Settings

- **Sign-in method**: Email only (no username)
- **Self-registration**: Enabled
- **Email verification**: Required
- **MFA**: Disabled (can be enabled for production)

### Custom Attributes

The User Pool includes two custom attributes:

1. **custom:company_name**
   - Type: String
   - Min length: 2 characters
   - Max length: 100 characters
   - Mutable: Yes
   - Required during sign-up

2. **custom:company_website**
   - Type: String
   - Min length: 5 characters
   - Max length: 200 characters
   - Mutable: Yes
   - Required during sign-up

### Password Policy

- Minimum length: 8 characters
- Requires lowercase letters
- Requires uppercase letters
- Requires numbers
- Requires symbols

### Account Recovery

- Method: Email only
- Users can reset passwords via email verification

## User Pool Client Configuration

### Client Type

- **Type**: Public client (no client secret)
- **Purpose**: Single Page Application (SPA)

### Authentication Flows

Enabled flows:
- `USER_PASSWORD_AUTH`: Username/password authentication
- `USER_SRP_AUTH`: Secure Remote Password protocol
- `REFRESH_TOKEN_AUTH`: Token refresh (automatic)

Disabled flows:
- `CUSTOM_AUTH`: Not used
- `ADMIN_USER_PASSWORD_AUTH`: Not used (admin-only)

### OAuth 2.0 Settings

**Grant Types**:
- Authorization Code Grant (enabled)
- Implicit Grant (disabled for security)

**Scopes**:
- `email`: Access to user's email
- `openid`: OpenID Connect support
- `profile`: Access to user profile

**Callback URLs** (Development):
- `http://localhost:5173/`
- `http://localhost:5173/app/dashboard`

**Logout URLs** (Development):
- `http://localhost:5173/`
- `http://localhost:5173/signin`

**Response Type**: `code` (Authorization Code)

### Token Validity

- **Access Token**: 1 hour
- **ID Token**: 1 hour
- **Refresh Token**: 30 days

## Identity Pool Configuration

### Purpose

The Identity Pool provides temporary AWS credentials to authenticated users, enabling:
- Direct API Gateway calls with IAM authentication
- Access to other AWS services (if needed)

### Configuration

- **Unauthenticated access**: Disabled
- **Authentication providers**: Cognito User Pool only

### IAM Roles

**Authenticated Role**:
- Assumed by authenticated Cognito users
- Permissions:
  - `mobileanalytics:PutEvents`: Analytics tracking
  - `cognito-sync:*`: Cognito Sync operations
  - `cognito-identity:*`: Identity Pool operations
- Trust policy: Federated principal with Cognito Identity Pool

The authenticated role is automatically attached to the Identity Pool and assumed when users sign in through Cognito.

## Integration with Frontend

### Amplify Configuration

The frontend uses AWS Amplify to integrate with Cognito. Configuration is stored in `amplify_outputs.json`:

```json
{
  "auth": {
    "user_pool_id": "us-east-1_XXXXXXXXX",
    "user_pool_client_id": "XXXXXXXXXXXXXXXXXXXXXXXXXX",
    "identity_pool_id": "us-east-1:XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
    "oauth": {
      "domain": "reinvent-planner.auth.us-east-1.amazoncognito.com",
      "scope": ["email", "openid", "profile"],
      "redirect_sign_in": "http://localhost:5173/",
      "redirect_sign_out": "http://localhost:5173/",
      "response_type": "code"
    }
  }
}
```

### Authentication Flow

1. **Sign Up**:
   - User provides email, password, company name, and company website
   - Cognito sends verification email
   - User clicks verification link
   - Account is activated

2. **Sign In**:
   - User provides email and password
   - Cognito validates credentials
   - Returns JWT tokens (access, ID, refresh)
   - Amplify stores tokens securely

3. **API Calls**:
   - Amplify automatically includes JWT token in Authorization header
   - API Gateway validates token with Cognito
   - Request is forwarded to Lambda if valid

4. **Token Refresh**:
   - Amplify automatically refreshes tokens before expiration
   - Uses refresh token to obtain new access/ID tokens
   - Transparent to the user

## API Gateway Integration

### CORS Configuration

API Gateway is configured to accept requests from the frontend:

```python
allowed_origins = [
    "http://localhost:5173",  # Local development
    "http://localhost:3000",  # Alternative local port
]

allow_headers = [
    "authorization",  # For Cognito JWT tokens
    "content-type",
    "x-amz-date",
    # ... other headers
]
```

### Authentication

- API Gateway validates JWT tokens from Cognito
- No additional authentication logic needed in Lambda functions
- User identity available in Lambda event context

## Security Considerations

### Development vs Production

**Current Configuration (Development)**:
- `RemovalPolicy.DESTROY`: Resources deleted when stack is destroyed
- Localhost callback URLs
- Permissive CORS (localhost origins)

**Production Recommendations**:
1. Change `RemovalPolicy` to `RETAIN` to prevent accidental deletion
2. Update callback/logout URLs to production domain
3. Restrict CORS to production domain only
4. Enable MFA for enhanced security
5. Implement account lockout policies
6. Enable advanced security features (compromised credentials detection)
7. Set up CloudWatch alarms for authentication failures
8. Implement proper logging and monitoring

### Token Security

- Tokens stored securely by Amplify (memory/secure storage)
- HTTPS required for all authentication flows
- Short token validity (1 hour) limits exposure
- Refresh tokens enable seamless re-authentication

### Custom Attributes Security

- Custom attributes are mutable (users can update)
- No sensitive data should be stored in custom attributes
- Consider encryption for sensitive company information
- Implement proper access controls in application logic

## Deployment

### Initial Deployment

1. Deploy CDK stack:
   ```bash
   cd iac
   cdk deploy
   ```

2. Generate Amplify configuration:
   ```bash
   python scripts/generate_amplify_config.py \
     --stack-name <stack-name> \
     --region <region>
   ```

3. Start frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Updating Configuration

If you modify Cognito settings in CDK:

1. Update `iac/iac/cognito_stack.py`
2. Redeploy: `cdk deploy`
3. Regenerate config: `python scripts/generate_amplify_config.py ...`
4. Restart frontend

## Troubleshooting

### Common Issues

**Issue**: "User pool does not exist"
- **Solution**: Verify User Pool ID in `amplify_outputs.json`
- Check CloudFormation outputs for correct ID

**Issue**: "Invalid redirect URI"
- **Solution**: Ensure callback URLs in Cognito match application URLs
- Check for trailing slashes and protocol (http vs https)

**Issue**: "Token validation failed"
- **Solution**: Verify User Pool Client ID is correct
- Ensure tokens haven't expired
- Check that client is configured as public (no secret)

**Issue**: "CORS error on authentication"
- **Solution**: Verify frontend origin in API Gateway CORS settings
- Ensure `authorization` header is in `allow_headers`

### Debugging

Enable debug logging in Amplify:

```typescript
import { Amplify } from 'aws-amplify'

Amplify.configure({
  // ... config
})

// Enable debug logging
window.LOG_LEVEL = 'DEBUG'
```

Check browser console for detailed authentication flow logs.

## Testing

### Manual Testing

1. **Sign Up Flow**:
   - Navigate to `/signup`
   - Enter email, password, company name, website
   - Check email for verification link
   - Click link to verify
   - Sign in with credentials

2. **Sign In Flow**:
   - Navigate to `/signin`
   - Enter email and password
   - Verify redirect to dashboard
   - Check that user info is displayed

3. **Token Refresh**:
   - Stay logged in for > 1 hour
   - Verify automatic token refresh
   - Ensure no interruption to user experience

4. **Sign Out**:
   - Click sign out
   - Verify redirect to sign-in page
   - Verify cannot access protected routes

### Automated Testing

Consider implementing:
- Unit tests for auth service methods
- Integration tests for sign-up/sign-in flows
- E2E tests with Cypress/Playwright

## Monitoring

### CloudWatch Metrics

Monitor these Cognito metrics:
- `UserAuthentication`: Sign-in attempts
- `UserAuthenticationSuccess`: Successful sign-ins
- `UserAuthenticationFailure`: Failed sign-ins
- `TokenRefreshSuccess`: Token refresh operations

### CloudWatch Logs

Enable and monitor:
- Cognito User Pool logs
- API Gateway access logs
- Lambda function logs

### Alarms

Set up alarms for:
- High authentication failure rate
- Unusual sign-up patterns
- Token refresh failures

## Cost Considerations

### Cognito Pricing

- **MAU (Monthly Active Users)**: First 50,000 free, then $0.0055/MAU
- **Advanced Security**: Additional cost if enabled
- **SMS MFA**: Per-message charges if enabled

### Optimization

- Use email verification (free) instead of SMS
- Implement proper token caching to reduce API calls
- Monitor and optimize token refresh patterns

## References

- [AWS Amplify Auth Documentation](https://docs.amplify.aws/react/build-a-backend/auth/)
- [Amazon Cognito Developer Guide](https://docs.aws.amazon.com/cognito/latest/developerguide/)
- [Cognito User Pool Custom Attributes](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-attributes.html)
- [OAuth 2.0 Authorization Code Flow](https://oauth.net/2/grant-types/authorization-code/)
