from aws_cdk import (
    # Duration,
    Stack,
    CfnOutput,
    # aws_sqs as sqs,
)

from aws_cdk import aws_apigateway as apigw
from constructs import Construct
from aws_cdk.aws_apigateway import RestApi, Cors

from .lambda_stack import LambdaStack
from .mcp_stack import MCPStack
from .strands_agent_stack import StrandsAgentStack
from .template_dynamo_table import TemplateDynamoTable
from .sessions_dynamo_table import SessionsDynamoTable
from .cognito_stack import CognitoStack
from .frontend_stack import FrontendStack


class TemplateStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define allowed origins for CORS (frontend origins)
        allowed_origins = [
            "http://localhost:5173",  # Local development
            "http://localhost:3000",  # Alternative local port
        ]
        
        self.rest_api = RestApi(self, "Reinvent_Planner",
                                    rest_api_name="Reinvent_Planner_RestApi",
                                    description="This is the Reinvent_Planner RestApi",
                                    default_cors_preflight_options=
                                    {
                                        "allow_origins": apigw.Cors.ALL_ORIGINS,
                                        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                                        "allow_headers": [
                                            *apigw.Cors.DEFAULT_HEADERS,
                                            "mcp-protocol-version",
                                            "mcp-session-id",
                                            "authorization"  # For Cognito JWT tokens
                                            ]
                                    },
                                )

        api_gateway_resource = self.rest_api.root.add_resource("mss-template", default_cors_preflight_options=
        {
            "allow_origins": allowed_origins,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                *apigw.Cors.DEFAULT_HEADERS,
                "mcp-protocol-version",
                "mcp-session-id",
                "authorization"  # For Cognito JWT tokens
            ]
        }
                                                               )

        # self.dynamo_table = TemplateDynamoTable(self, "Dynamo_Table")
        self.sessions_dynamo_table = SessionsDynamoTable(self, "SessionsDynamoTable")
        
        # Create Cognito stack for frontend authentication
        # Pass stack name to create unique domain prefix
        self.cognito_stack = CognitoStack(
            self, 
            "CognitoStack",
            stack_name=construct_id
        )
        
        # Create Cognito authorizer for API Gateway
        self.cognito_authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, "CognitoAuthorizer",
            cognito_user_pools=[self.cognito_stack.user_pool],
            authorizer_name="reinvent-planner-authorizer",
            identity_source="method.request.header.Authorization"
        )

        ENVIRONMENT_VARIABLES = {
            "STAGE": "DEV",
            "DYNAMO_TABLE_NAME": self.sessions_dynamo_table.table.table_name,
            "DYNAMO_PARTITION_KEY": "PK",
            "DYNAMO_SORT_KEY": "SK",
            "SESSIONS_DYNAMO_TABLE_NAME": self.sessions_dynamo_table.table.table_name,
            "SESSIONS_DYNAMO_PARTITION_KEY": "PK",
            "REGION": self.region,
        }



        self.lambda_stack = LambdaStack(self, api_gateway_resource=api_gateway_resource,
                                        environment_variables=ENVIRONMENT_VARIABLES, region=self.region)

        for function in self.lambda_stack.functions_that_need_dynamo_permissions:
            self.dynamo_table.table.grant_read_write_data(function)

        for function in self.lambda_stack.functions_that_need_sessions_dynamo_permissions:
            self.sessions_dynamo_table.table.grant_read_write_data(function)


        # Create MCP and Strands Agent stacks without URL dependencies
        self.mcp_stack = MCPStack(
            self,
            api_gateway_resource=api_gateway_resource,
            environment_variables=ENVIRONMENT_VARIABLES,
            dependencies_layers=self.lambda_stack.external_dependencies_layer,
            region=self.region
        )

        # Create FrontendStack first to get CloudFront URL
        self.frontend_stack = FrontendStack(
            self,
            construct_id="FrontendStack",
            stack_name=construct_id,
            region=self.region
        )
        
        # Add frontend URL to environment variables for agent CORS
        agent_environment_variables = ENVIRONMENT_VARIABLES.copy()
        agent_environment_variables["FRONTEND_URL"] = f"https://{self.frontend_stack.distribution.distribution_domain_name}"
        
        self.strands_agent_stack = StrandsAgentStack(
            self,
            api_gateway_resource=api_gateway_resource,
            environment_variables=agent_environment_variables,
            powertools_layer=self.lambda_stack.lambda_power_tools,
            region=self.region,
            cognito_authorizer=self.cognito_authorizer
        )

        
        # Now that all resources are created, output the API Gateway URLs
        # These use url_for_path which is safe after all integrations are complete
        CfnOutput(
            self, "ApiGatewayBaseUrl",
            value=f"https://{self.rest_api.rest_api_id}.execute-api.{self.region}.amazonaws.com/prod/mss-template",
            description="API Gateway base URL for all endpoints"
        )
        
        CfnOutput(
            self, "McpEndpointUrl",
            value=f"https://{self.rest_api.rest_api_id}.execute-api.{self.region}.amazonaws.com/prod/mss-template/mcp",
            description="MCP server endpoint URL"
        )
        
        CfnOutput(
            self, "StrandsAgentUrl",
            value=f"https://{self.rest_api.rest_api_id}.execute-api.{self.region}.amazonaws.com/prod/mss-template/agent",
            description="Strands Agent endpoint URL"
        )
        
        CfnOutput(
            self, "SessionsApiUrl",
            value=f"https://{self.rest_api.rest_api_id}.execute-api.{self.region}.amazonaws.com/prod/mss-template/sessions",
            description="Sessions API endpoint URL (requires Cognito authentication)"
        )

        