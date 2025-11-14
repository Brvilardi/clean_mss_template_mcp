import sys
from pathlib import Path

# Add project root to Python path for direct script execution
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import boto3
import dotenv



def setup_dynamo_table():
    """
    Creates the Sessions DynamoDB table in local DynamoDB with GSIs.
    Table structure:
    - PK only (no SK)
    - GSI-Venue: venue_name (PK), start_datetime (SK)
    - GSI-Day: day (PK), start_datetime (SK)
    - GSI-Level: level_value (PK), start_datetime (SK)
    """
    dynamo_table_name = "sessions_mss_template-table"
    endpoint_url = "http://localhost:8000"
    print("Setting up Sessions DynamoDB table...")

    dynamo_client = boto3.client('dynamodb', endpoint_url=endpoint_url)
    print("DynamoDB client created")
    tables = dynamo_client.list_tables()['TableNames']

    if dynamo_table_name not in tables:
        print("Creating sessions table...")
        dynamo_client.create_table(
            TableName=dynamo_table_name,
            KeySchema=[
                {
                    'AttributeName': 'PK',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'PK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'venue_name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'day',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'level_value',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'short_id',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'start_datetime',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'GSI-Venue',
                    'KeySchema': [
                        {
                            'AttributeName': 'venue_name',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'start_datetime',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'GSI-Day',
                    'KeySchema': [
                        {
                            'AttributeName': 'day',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'start_datetime',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'GSI-shortId',
                    'KeySchema': [
                        {
                            'AttributeName': 'short_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'start_datetime',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'GSI-Level',
                    'KeySchema': [
                        {
                            'AttributeName': 'level_value',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'start_datetime',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ],
            BillingMode='PAY_PER_REQUEST',
        )
        print("Waiting for table to be created...")
        dynamo_client.get_waiter('table_exists').wait(TableName=dynamo_table_name)

        print('Sessions table created!')

    else:
        print("Sessions table already exists!")


def load_mock_to_local_dynamo():
    """
    Loads mock session data from SessionRepositoryMock into local DynamoDB.
    Uses the SessionDynamoDTO for proper data conversion.
    
    Note: This script requires SessionRepositoryDynamo and SessionDynamoDTO
    to be implemented first (tasks 2 and 3 in the migration plan).
    """
    setup_dynamo_table()
    
    try:
        # Import here to avoid circular dependencies
        from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock
        from src.shared.infra.repositories.session_repository_dynamo import SessionRepositoryDynamo
        from src.shared.infra.dto.session_dynamo_dto import SessionDynamoDTO
    except ImportError as e:
        print(f"Error: Required modules not yet implemented: {e}")
        print("Please complete tasks 2 and 3 (SessionDynamoDTO and SessionRepositoryDynamo) first.")
        return
    
    mock_repo = SessionRepositoryMock()
    dynamo_repo = SessionRepositoryDynamo()

    count = 0

    print('Loading mock session data to dynamo...')
    for session in mock_repo.get_all_sessions():
        print(f"Loading session {session.session_id} | {session.title} to dynamo")
        # Use the repository's internal method to store the session
        # This will use SessionDynamoDTO for proper conversion
        session_dto = SessionDynamoDTO.from_entity(session)
        dynamo_item = session_dto.to_dynamo()
        
        # Add partition key to the item
        pk = SessionRepositoryDynamo.partition_key_format(session.session_id)
        dynamo_item[dynamo_repo.dynamo.partition_key] = pk
        
        # Use batch_write_items for efficiency (will be batched automatically)
        dynamo_repo.dynamo.dynamo_table.put_item(Item=dynamo_item)
        count += 1

    print(f"{count} sessions loaded to dynamo!")


if __name__ == '__main__':
    dotenv.load_dotenv()
    load_mock_to_local_dynamo()
