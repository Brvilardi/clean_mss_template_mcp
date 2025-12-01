import os
from aws_cdk import (
    aws_lambda as lambda_,
    NestedStack, Duration
)
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from constructs import Construct
from aws_cdk.aws_apigateway import Resource, LambdaIntegration


class LambdaStack(Construct):
    functions_that_need_dynamo_permissions = []
    functions_that_need_sessions_dynamo_permissions = []

    def create_lambda_api_gateway_integration(self, module_name: str, method: str, mss_student_api_resource: Resource,
                                              environment_variables: dict = {"STAGE": "TEST"}, memory_size: int = 128,
                                              timeout_seconds: int = 15, needs_external_deps: bool = False):
        layers = [self.lambda_layer, self.lambda_power_tools]
        if needs_external_deps:
            layers.append(self.external_dependencies_layer)
        
        function = lambda_.Function(
            self, module_name.title(),
            code=lambda_.Code.from_asset(f"../src/modules/{module_name}"),
            handler=f"app.{module_name}_presenter.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_14,
            architecture=lambda_.Architecture.ARM_64,
            layers=layers,
            environment=environment_variables,
            memory_size=memory_size,
            timeout=Duration.seconds(timeout_seconds),
            tracing=lambda_.Tracing.ACTIVE
        )

        mss_student_api_resource.add_resource(module_name.replace("_", "-")).add_method(method,
                                                                                        integration=LambdaIntegration(
                                                                                            function))

        return function

    def __init__(self, scope: Construct, api_gateway_resource: Resource, environment_variables: dict, region: str) -> None:
        super().__init__(scope, "Template_Lambdas")

        self.lambda_layer = lambda_.LayerVersion(self, "Template_Layer",
                                                 code=lambda_.Code.from_asset("./lambda_layer_out_temp"),
                                                 compatible_runtimes=[lambda_.Runtime.PYTHON_3_14]
                                                 )

        # Powertools layer for ARM64 - version 68 is for Python 3.13+
        self.lambda_power_tools = lambda_.LayerVersion.from_layer_version_arn(
            self, "Lambda_Power_Tools", 
            layer_version_arn=f"arn:aws:lambda:{region}:017000801446:layer:AWSLambdaPowertoolsPythonV2-Arm64:68"
        )
        
        self.external_dependencies_layer = PythonLayerVersion(
            self, "External_Dependencies_Layer",
            entry="./lambda_external_dependencies",
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_14],
            compatible_architectures=[lambda_.Architecture.ARM_64],
            description="Layer with external dependencies like requests"
        )

        self.get_all_sessions_function = self.create_lambda_api_gateway_integration(
            module_name="get_all_sessions",
            method="GET",
            mss_student_api_resource=api_gateway_resource,
            environment_variables=environment_variables,
            memory_size=512,
            timeout_seconds=30,
            needs_external_deps=True
        )

        self.sync_sessions_function = self.create_lambda_api_gateway_integration(
            module_name="sync_sessions",
            method="POST",
            mss_student_api_resource=api_gateway_resource,
            environment_variables=environment_variables,
            memory_size=512,
            timeout_seconds=30,
            needs_external_deps=True
        )

        self.get_sessions_by_venue_function = self.create_lambda_api_gateway_integration(
            module_name="get_sessions_by_venue",
            method="GET",
            mss_student_api_resource=api_gateway_resource,
            environment_variables=environment_variables,
            needs_external_deps=True,
            memory_size=512,
            timeout_seconds=30
        )

        self.get_sessions_by_day_function = self.create_lambda_api_gateway_integration(
            module_name="get_sessions_by_day",
            method="GET",
            mss_student_api_resource=api_gateway_resource,
            environment_variables=environment_variables,
            needs_external_deps=True,
            memory_size=512,
            timeout_seconds=30
        )

        self.get_sessions_by_level_function = self.create_lambda_api_gateway_integration(
            module_name="get_sessions_by_level",
            method="GET",
            mss_student_api_resource=api_gateway_resource,
            environment_variables=environment_variables,
            needs_external_deps=True,
            memory_size=512,
            timeout_seconds=30
        )

        self.get_sessions_by_short_id_function = self.create_lambda_api_gateway_integration(
            module_name="get_sessions_by_short_id",
            method="GET",
            mss_student_api_resource=api_gateway_resource,
            environment_variables=environment_variables,
            needs_external_deps=True,
            memory_size=512,
            timeout_seconds=30
        )

        self.get_all_sessions_paginated_function = self.create_lambda_api_gateway_integration(
            module_name="get_all_sessions_paginated",
            method="GET",
            mss_student_api_resource=api_gateway_resource,
            environment_variables=environment_variables,
            needs_external_deps=True,
            memory_size=512,
            timeout_seconds=30
        )

        self.search_sessions_function = self.create_lambda_api_gateway_integration(
            module_name="search_sessions",
            method="GET",
            mss_student_api_resource=api_gateway_resource,
            environment_variables=environment_variables,
            needs_external_deps=True,
            memory_size=512,
            timeout_seconds=10
        )

        self.functions_that_need_dynamo_permissions = []

        self.functions_that_need_sessions_dynamo_permissions = [self.get_all_sessions_function,
                                                                 self.sync_sessions_function,
                                                                 self.get_sessions_by_venue_function,
                                                                 self.get_sessions_by_day_function,
                                                                 self.get_sessions_by_level_function,
                                                                 self.get_sessions_by_short_id_function,
                                                                 self.get_all_sessions_paginated_function,
                                                                 self.search_sessions_function]
