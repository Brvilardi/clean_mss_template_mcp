from aws_cdk import (
    aws_dynamodb as dynamodb,
    RemovalPolicy,
)
from constructs import Construct


class SessionsDynamoTable(Construct):
    """
    DynamoDB table construct for storing re:Invent sessions.
    
    This table uses a single partition key (PK) without a sort key,
    and includes four Global Secondary Indexes for optimized queries:
    - GSI-Venue: Query sessions by venue
    - GSI-Day: Query sessions by day
    - GSI-Level: Query sessions by level
    - GSI-ShortId: Query sessions by short_id for quick lookups
    """
    table: dynamodb.Table

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create table with only partition key (no sort key)
        self.table = dynamodb.Table(
            self, "SessionsDynamoTable",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # GSI-Venue: Query sessions by venue, sorted by start time
        self.table.add_global_secondary_index(
            index_name="GSI-Venue",
            partition_key=dynamodb.Attribute(
                name="venue_name",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="start_datetime",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # GSI-Day: Query sessions by day, sorted by start time
        self.table.add_global_secondary_index(
            index_name="GSI-Day",
            partition_key=dynamodb.Attribute(
                name="day",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="start_datetime",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # GSI-Level: Query sessions by level value, sorted by start time
        self.table.add_global_secondary_index(
            index_name="GSI-Level",
            partition_key=dynamodb.Attribute(
                name="level_value",
                type=dynamodb.AttributeType.NUMBER
            ),
            sort_key=dynamodb.Attribute(
                name="start_datetime",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # GSI-ShortId: Query sessions by short_id for quick lookups
        self.table.add_global_secondary_index(
            index_name="GSI-ShortId",
            partition_key=dynamodb.Attribute(
                name="short_id",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )
