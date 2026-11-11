import os
from aws_cdk import (
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_logs as logs,
    Duration
)
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from constructs import Construct
from aws_cdk.aws_apigateway import Resource, LambdaIntegration, Cors, AuthorizationType
from aws_cdk import aws_bedrockagentcore as agentcore

class StrandsAgentStack(Construct):
    """CDK stack for Strands re:Invent agent deployed as Lambda function with Lambda Web Adapter."""

    # AWS Lambda Web Adapter Layer ARN (ARM64)
    LAMBDA_WEB_ADAPTER_LAYER_ARN = lambda region: (
        f"arn:aws:lambda:{region}:753240598075:layer:LambdaAdapterLayerArm64:25"
    )



    def __init__(
        self,
        scope: Construct,
        api_gateway_resource: Resource,
        environment_variables: dict,
        powertools_layer,
        region: str,
        cognito_authorizer=None
    ) -> None:
        super().__init__(scope, "StrandsAgent")
        
        # Store cognito_authorizer for use in method creation
        self.cognito_authorizer = cognito_authorizer


        # Create AgentCore Memory
        self.memory = agentcore.CfnMemory(
            self, "SessionsAgentMemory",
            name="SessionsMemory",
            description="Memory with built-in LTM strategies",
            event_expiry_duration=20,
            memory_strategies=[
                agentcore.CfnMemory.MemoryStrategyProperty(
                    summary_memory_strategy=agentcore.CfnMemory.SummaryMemoryStrategyProperty(
                        name="SummaryMemory",
                        namespaces=["/strategies/{memoryStrategyId}/actors/{actorId}/sessions/{sessionId}"]
                    ),
                ),
                agentcore.CfnMemory.MemoryStrategyProperty(
                    semantic_memory_strategy=agentcore.CfnMemory.SemanticMemoryStrategyProperty(
                        name="SemanticMemory",
                        namespaces=["/strategies/{memoryStrategyId}/actors/{actorId}"]
                    )
                )
            ],
        )

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
        envs['MEMORY_ID'] = self.memory.attr_memory_id

        # Create Lambda function (without API Gateway integration yet)
        self.agent_function = lambda_.Function(
            self, "StrandsAgentFunction",
            code=lambda_.Code.from_asset("../src/strands-agent"),
            handler="run.sh",
            runtime=lambda_.Runtime.PYTHON_3_14,
            architecture=lambda_.Architecture.ARM_64,
            layers=self.layers,
            environment=envs,
            memory_size=3008,  # Increased for better performance
            timeout=Duration.seconds(120),  # Increased timeout for agent processing
            tracing=lambda_.Tracing.ACTIVE,
            snap_start=lambda_.SnapStartConf.ON_PUBLISHED_VERSIONS
        )
        
        # Add MCP_ENDPOINT after function is created to avoid circular dependency
        # This will be resolved at deployment time
        self.agent_function.add_environment(
            "MCP_ENDPOINT",
            f"https://{api_gateway_resource.api.rest_api_id}.execute-api.{region}.amazonaws.com/prod/mss-template/mcp"
        )
        
        # Create a published version for SnapStart
        self.agent_function_version = self.agent_function.current_version
        
        # Create an alias pointing to the version
        self.agent_function_alias = lambda_.Alias(
            self, "StrandsAgentAlias",
            alias_name="live",
            version=self.agent_function_version
        )
        
        # Create API Gateway integration using the alias
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
            "ANY",
            integration=LambdaIntegration(self.agent_function_alias),
            authorizer=self.cognito_authorizer,
            authorization_type=AuthorizationType.COGNITO if self.cognito_authorizer else None
        )
        
        # Add proxy resource to handle all sub-paths like /agent/ping, /agent/invocations
        agent_resource.add_proxy(
            default_integration=LambdaIntegration(self.agent_function_alias),
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
            },
            default_method_options={
                "authorizer": self.cognito_authorizer,
                "authorization_type": AuthorizationType.COGNITO if self.cognito_authorizer else None
            }
        )

        # Grant Bedrock permissions
        self.agent_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock-agentcore:ListEvents",
                    "bedrock-agentcore:CreateEvent",
                    "bedrock-agentcore:GetEvent",
                    "bedrock-agentcore:DeleteEvent"
                ],
                resources=["*"]
            )
        )

        # Create BFF Lambda function for retrieving chat history
        # This function aggregates session data from AgentCore Memory for the frontend
        bff_envs = environment_variables.copy()
        bff_envs['MEMORY_ID'] = self.memory.attr_memory_id
        bff_envs['POWERTOOLS_SERVICE_NAME'] = 'chat-history'
        bff_envs['POWERTOOLS_METRICS_NAMESPACE'] = 'StrandsAgent'
        bff_envs['LOG_LEVEL'] = 'INFO'
        # Note: AWS_REGION is reserved by Lambda runtime, so we don't set it manually
        # The Lambda function can access the region via the AWS_REGION environment variable automatically
        
        self.chat_history_function = lambda_.Function(
            self, "ChatHistoryFunction",
            code=lambda_.Code.from_asset("../src/strands-agent"),
            handler="chat_history_handler.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_14,
            architecture=lambda_.Architecture.ARM_64,
            layers=[powertools_layer],
            environment=bff_envs,
            memory_size=512,
            timeout=Duration.seconds(30),
            tracing=lambda_.Tracing.ACTIVE,
            description="BFF Lambda for retrieving chat history from AgentCore Memory"
        )
        
        # Grant Bedrock AgentCore Memory permissions for retrieving chat history
        self.chat_history_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock-agentcore:ListEvents",
                    "bedrock-agentcore:GetEvent"
                ],
                resources=[self.memory.attr_memory_arn]
            )
        )
        
        # Create API Gateway resource for sessions endpoint
        sessions_resource = api_gateway_resource.add_resource(
            "chat_history",
            default_cors_preflight_options={
                "allow_origins": Cors.ALL_ORIGINS,
                "allow_methods": ["GET", "OPTIONS"],
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
        
        # Add GET method with Lambda integration and Cognito authorizer
        sessions_resource.add_method(
            "GET",
            integration=LambdaIntegration(self.chat_history_function),
            authorizer=cognito_authorizer,
            authorization_type=AuthorizationType.COGNITO if cognito_authorizer else None
        )
