from aws_cdk import (
    aws_cognito as cognito,
    aws_iam as iam,
    RemovalPolicy,
    CfnOutput,
    Duration
)
from constructs import Construct


class CognitoStack(Construct):
    """CDK construct for Cognito User Pool and Identity Pool for frontend authentication."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        stack_name: str,
        cloudfront_url: str = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id)
        
        # Create unique domain prefix using stack name
        # Remove special characters and convert to lowercase
        domain_prefix = f"reinvent-planner-{stack_name.lower().replace('_', '-')}"
        
        # Build callback and logout URLs
        # Always include localhost for local development
        callback_urls = [
            "http://localhost:5173/",
            "http://localhost:5173/app/dashboard"
        ]
        logout_urls = [
            "http://localhost:5173/",
            "http://localhost:5173/signin"
        ]
        
        # Add CloudFront URLs if provided (for production deployment)
        if cloudfront_url:
            callback_urls.extend([
                f"{cloudfront_url}/",
                f"{cloudfront_url}/app/dashboard"
            ])
            logout_urls.extend([
                f"{cloudfront_url}/",
                f"{cloudfront_url}/signin"
            ])

        # Create User Pool with custom attributes
        self.user_pool = cognito.UserPool(
            self, "ReInventPlannerUserPool",
            user_pool_name="reinvent-planner-user-pool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                username=False
            ),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(
                    required=True,
                    mutable=True
                )
            ),
            custom_attributes={
                "company_name": cognito.StringAttribute(
                    min_len=2,
                    max_len=100,
                    mutable=True
                ),
                "company_website": cognito.StringAttribute(
                    min_len=5,
                    max_len=200,
                    mutable=True
                )
            },
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=RemovalPolicy.DESTROY  # For dev/test - change for production
        )

        # Create User Pool Client for the frontend application
        self.user_pool_client = self.user_pool.add_client(
            "ReInventPlannerWebClient",
            user_pool_client_name="reinvent-planner-web-client",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
                custom=False,
                admin_user_password=False
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=False
                ),
                scopes=[
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.PROFILE
                ],
                callback_urls=callback_urls,
                logout_urls=logout_urls
            ),
            prevent_user_existence_errors=True,
            generate_secret=False,  # Public client for SPA
            access_token_validity=Duration.hours(1),
            id_token_validity=Duration.hours(1),
            refresh_token_validity=Duration.days(30)
        )

        # Create User Pool Domain for OAuth with unique prefix
        self.user_pool_domain = self.user_pool.add_domain(
            "ReInventPlannerDomain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=domain_prefix
            )
        )

        # Create Identity Pool for AWS credentials
        self.identity_pool = cognito.CfnIdentityPool(
            self, "ReInventPlannerIdentityPool",
            identity_pool_name="reinvent-planner-identity-pool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[
                cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                    client_id=self.user_pool_client.user_pool_client_id,
                    provider_name=self.user_pool.user_pool_provider_name
                )
            ]
        )

        # Create IAM role for authenticated users
        self.authenticated_role = iam.Role(
            self, "CognitoAuthenticatedRole",
            assumed_by=iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                {
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": self.identity_pool.ref
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "authenticated"
                    }
                },
                "sts:AssumeRoleWithWebIdentity"
            ),
            description="Role for authenticated Cognito users"
        )

        # Add basic permissions for authenticated users
        self.authenticated_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "mobileanalytics:PutEvents",
                    "cognito-sync:*",
                    "cognito-identity:*"
                ],
                resources=["*"]
            )
        )

        # Attach roles to Identity Pool
        cognito.CfnIdentityPoolRoleAttachment(
            self, "IdentityPoolRoleAttachment",
            identity_pool_id=self.identity_pool.ref,
            roles={
                "authenticated": self.authenticated_role.role_arn
            }
        )

        # Output values for amplify_outputs.json
        CfnOutput(
            self, "UserPoolId",
            value=self.user_pool.user_pool_id,
            description="Cognito User Pool ID"
        )

        CfnOutput(
            self, "UserPoolClientId",
            value=self.user_pool_client.user_pool_client_id,
            description="Cognito User Pool Client ID"
        )

        CfnOutput(
            self, "IdentityPoolId",
            value=self.identity_pool.ref,
            description="Cognito Identity Pool ID"
        )

        CfnOutput(
            self, "UserPoolDomain",
            value=f"{self.user_pool_domain.domain_name}.auth.{scope.region}.amazoncognito.com",
            description="Cognito User Pool Domain"
        )
