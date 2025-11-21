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

    def create_lambda_api_gateway_integration(self, method: str, mss_student_api_resource: Resource,
                                              environment_variables: dict = {"STAGE": "TEST"}, memory_size: int = 128,
                                              timeout_seconds: int = 15, layers: list = None):
        function = lambda_.Function(
            self, "MCP_SERVER",
            code=lambda_.Code.from_asset(f"../src/mcp"),
            handler=f"run.sh",
            runtime=lambda_.Runtime.PYTHON_3_14,
            architecture=lambda_.Architecture.ARM_64,
            layers=layers,
            environment=environment_variables,
            memory_size=memory_size,
            timeout=Duration.seconds(timeout_seconds),
            tracing=lambda_.Tracing.ACTIVE,
            snap_start=lambda_.SnapStartConf.ON_PUBLISHED_VERSIONS
        )

        mss_student_api_resource.add_resource("mcp").add_method(method,
                                                                        integration=LambdaIntegration(
                                                                                            function))


        return function

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

        self.mcp_server = self.create_lambda_api_gateway_integration(
            method="ANY",
            mss_student_api_resource=api_gateway_resource,
            environment_variables=envs,
            memory_size=3008,  # Increased for better performance
            timeout_seconds=60,  # Increased timeout for complex queries
            layers=self.layers
        )
        
        # Add API_GATEWAY_BASE_URL after function is created to avoid circular dependency
        # This will be resolved at deployment time
        self.mcp_server.add_environment(
            "API_GATEWAY_BASE_URL",
            f"https://{api_gateway_resource.api.rest_api_id}.execute-api.{region}.amazonaws.com/prod/mss-template"
        )


