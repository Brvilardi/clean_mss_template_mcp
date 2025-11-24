import os
from aws_cdk import (
    aws_lambda as lambda_,
    aws_iam as iam,
    Duration
)
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from constructs import Construct
from aws_cdk.aws_apigateway import Resource, LambdaIntegration, Cors


class StrandsAgentStack(Construct):
    """CDK stack for Strands re:Invent agent deployed as Lambda function with Lambda Web Adapter."""

    # AWS Lambda Web Adapter Layer ARN (ARM64)
    LAMBDA_WEB_ADAPTER_LAYER_ARN = lambda region: (
        f"arn:aws:lambda:{region}:753240598075:layer:LambdaAdapterLayerArm64:25"
    )

    def create_lambda_api_gateway_integration(
        self,
        method: str,
        api_gateway_resource: Resource,
        environment_variables: dict,
        memory_size: int = 512,
        timeout_seconds: int = 30,
        layers: list = None
    ):
        """
        Create Lambda function with API Gateway integration.

        Args:
            method: HTTP method (e.g., "ANY")
            api_gateway_resource: API Gateway resource to attach to
            environment_variables: Environment variables for Lambda
            memory_size: Lambda memory in MB
            timeout_seconds: Lambda timeout in seconds
            layers: Lambda layers to attach

        Returns:
            Lambda function
        """
        function = lambda_.Function(
            self, "StrandsAgentFunction",
            code=lambda_.Code.from_asset("../src/strands-agent"),
            handler="run.sh",
            runtime=lambda_.Runtime.PYTHON_3_14,
            architecture=lambda_.Architecture.ARM_64,
            layers=layers,
            environment=environment_variables,
            memory_size=memory_size,
            timeout=Duration.seconds(timeout_seconds),
            tracing=lambda_.Tracing.ACTIVE,
            snap_start=lambda_.SnapStartConf.ON_PUBLISHED_VERSIONS
        )

        # Create API Gateway resource with proxy for all sub-paths
        agent_resource = api_gateway_resource.add_resource(
            "agent",
            default_cors_preflight_options={
                "allow_origins": Cors.ALL_ORIGINS,
                "allow_methods": Cors.ALL_METHODS,
                "allow_headers": [
                    "Content-Type",
                    "Authorization",
                    "X-Amz-Date",
                    "X-Api-Key",
                    "X-Amz-Security-Token",
                    "X-Amz-User-Agent"
                ],
                "allow_credentials": False
            }
        )
        agent_resource.add_method(
            method,
            integration=LambdaIntegration(function)
        )
        
        # Add proxy resource to handle all sub-paths like /agent/ping, /agent/invocations
        agent_resource.add_proxy(
            default_integration=LambdaIntegration(function),
            any_method=True,
            default_cors_preflight_options={
                "allow_origins": Cors.ALL_ORIGINS,
                "allow_methods": Cors.ALL_METHODS,
                "allow_headers": [
                    "Content-Type",
                    "Authorization",
                    "X-Amz-Date",
                    "X-Api-Key",
                    "X-Amz-Security-Token",
                    "X-Amz-User-Agent"
                ],
                "allow_credentials": False
            }
        )

        return function

    def __init__(
        self,
        scope: Construct,
        api_gateway_resource: Resource,
        environment_variables: dict,
        powertools_layer,
        region: str
    ) -> None:
        super().__init__(scope, "StrandsAgent")

        # Create agent-specific dependencies layer
        self.agent_dependencies_layer = PythonLayerVersion(
            self, "Agent_Dependencies_Layer",
            entry="./lambda_agent_dependencies",
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_14],
            compatible_architectures=[lambda_.Architecture.ARM_64],
            description="Layer with Strands Agent dependencies (strands, fastapi, pydantic v2)"
        )

        # Get Lambda Web Adapter layer
        self.lambda_web_adapter_layer = PythonLayerVersion.from_layer_version_arn(
            self, "LambdaWebAdapterLayer",
            StrandsAgentStack.LAMBDA_WEB_ADAPTER_LAYER_ARN(region)
        )

        # Combine layers - powertools, Lambda Web Adapter, then agent dependencies LAST
        # IMPORTANT: Agent dependencies must be last so Python finds the correct Pydantic v2
        self.layers = []
        self.layers.append(powertools_layer)
        self.layers.append(self.lambda_web_adapter_layer)
        self.layers.append(self.agent_dependencies_layer)

        # Configure environment variables for Lambda Web Adapter
        envs = environment_variables.copy()
        envs['AWS_LAMBDA_EXEC_WRAPPER'] = "/opt/bootstrap"  # Lambda Web Adapter bootstrap
        envs['AWS_LWA_PORT'] = "8000"  # Port for FastAPI
        envs['AWS_LWA_REMOVE_BASE_PATH'] = "/mss-template/agent"  # Remove API Gateway base path including /agent

        # Create Lambda function with API Gateway integration
        self.agent_function = self.create_lambda_api_gateway_integration(
            method="ANY",
            api_gateway_resource=api_gateway_resource,
            environment_variables=envs,
            memory_size=3008,  # Increased for better performance
            timeout_seconds=120,  # Increased timeout for agent processing
            layers=self.layers
        )
        
        # Add MCP_ENDPOINT after function is created to avoid circular dependency
        # This will be resolved at deployment time
        self.agent_function.add_environment(
            "MCP_ENDPOINT",
            f"https://{api_gateway_resource.api.rest_api_id}.execute-api.{region}.amazonaws.com/prod/mss-template/mcp"
        )

        # Grant Bedrock permissions
        self.agent_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                resources=["*"]
            )
        )
