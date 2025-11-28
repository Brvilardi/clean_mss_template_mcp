import os
from aws_cdk import (
    aws_lambda as lambda_,
    NestedStack, Duration
)
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from constructs import Construct
from aws_cdk.aws_apigateway import Resource, LambdaIntegration


class MCPStack(Construct):

    LAMBDA_WEB_ADAPTER_LAYER_ARN = lambda x: f"arn:aws:lambda:{x}:753240598075:layer:LambdaAdapterLayerArm64:25"



    def __init__(self, scope: Construct, api_gateway_resource: Resource, environment_variables: dict, dependencies_layers, region) -> None:
        super().__init__(scope, "Template_MCP")

        self.lambda_web_adapter_layer = PythonLayerVersion.from_layer_version_arn(
            self, "LambdaWebAdapterLayer",
            MCPStack.LAMBDA_WEB_ADAPTER_LAYER_ARN(region)
        )

        self.layers = []
        self.layers.append(dependencies_layers)
        self.layers.append(self.lambda_web_adapter_layer)

        envs = environment_variables.copy()
        envs['AWS_LAMBDA_EXEC_WRAPPER'] = "/opt/bootstrap" # set location for the other layers to work
        envs['AWS_LWA_PORT'] = "8000" # set the port to handle FastMCP requests
        envs['AWS_LWA_REMOVE_BASE_PATH'] = "/mss-template" #remove the apigateway base path

        # Create Lambda function
        self.mcp_server = lambda_.Function(
            self, "MCP_SERVER",
            code=lambda_.Code.from_asset("../src/mcp"),
            handler="run.sh",
            runtime=lambda_.Runtime.PYTHON_3_14,
            architecture=lambda_.Architecture.ARM_64,
            layers=self.layers,
            environment=envs,
            memory_size=3008,  # Increased for better performance
            timeout=Duration.seconds(60),  # Increased timeout for complex queries
            tracing=lambda_.Tracing.ACTIVE,
            snap_start=lambda_.SnapStartConf.ON_PUBLISHED_VERSIONS
        )
        
        # Add API_GATEWAY_BASE_URL after function is created to avoid circular dependency
        # This will be resolved at deployment time
        self.mcp_server.add_environment(
            "API_GATEWAY_BASE_URL",
            f"https://{api_gateway_resource.api.rest_api_id}.execute-api.{region}.amazonaws.com/prod/mss-template"
        )
        
        # Create a published version for SnapStart
        self.mcp_server_version = self.mcp_server.current_version
        
        # Create an alias pointing to the version
        self.mcp_server_alias = lambda_.Alias(
            self, "MCPServerAlias",
            alias_name="live",
            version=self.mcp_server_version
        )
        
        # Create API Gateway integration using the alias
        api_gateway_resource.add_resource("mcp").add_method(
            "ANY",
            integration=LambdaIntegration(self.mcp_server_alias)
        )


