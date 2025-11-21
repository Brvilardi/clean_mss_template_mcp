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


class TemplateStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.rest_api = RestApi(self, "Template_RestApi",
                                    rest_api_name="Template_RestApi",
                                    description="This is the Template RestApi",
                                    default_cors_preflight_options=
                                    {
                                        "allow_origins": Cors.ALL_ORIGINS,
                                        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                                        "allow_headers": [
                                            *apigw.Cors.DEFAULT_HEADERS,
                                            "mcp-protocol-version",
                                            "mcp-session-id"
                                            ]
                                    },
                                )

        api_gateway_resource = self.rest_api.root.add_resource("mss-template", default_cors_preflight_options=
        {
            "allow_origins": Cors.ALL_ORIGINS,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                *apigw.Cors.DEFAULT_HEADERS,
                "mcp-protocol-version",
                "mcp-session-id"
            ]
        }
                                                               )

        self.dynamo_table = TemplateDynamoTable(self, "TemplateDynamoTable")
        self.sessions_dynamo_table = SessionsDynamoTable(self, "SessionsDynamoTable")

        ENVIRONMENT_VARIABLES = {
            "STAGE": "DEV",
            "DYNAMO_TABLE_NAME": self.dynamo_table.table.table_name,
            "DYNAMO_PARTITION_KEY": "PK",
            "DYNAMO_SORT_KEY": "SK",
            "SESSIONS_DYNAMO_TABLE_NAME": self.sessions_dynamo_table.table.table_name,
            "SESSIONS_DYNAMO_PARTITION_KEY": "PK",
            "REGION": self.region,
        }



        self.lambda_stack = LambdaStack(self, api_gateway_resource=api_gateway_resource,
                                        environment_variables=ENVIRONMENT_VARIABLES)

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

        self.strands_agent_stack = StrandsAgentStack(
            self,
            api_gateway_resource=api_gateway_resource,
            environment_variables=ENVIRONMENT_VARIABLES,
            dependencies_layer=self.lambda_stack.external_dependencies_layer,
            region=self.region
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

        