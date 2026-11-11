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


def sync_sessions_from_api_to_dynamo():
    """
    Fetches sessions from the re:invent catalog API and loads them into DynamoDB Local.
    Uses the SessionRepositoryDynamo.sync_sessions_from_api() method.
    """
    setup_dynamo_table()
    
    try:
        # Import here to avoid circular dependencies
        from src.shared.infra.repositories.session_repository_dynamo import SessionRepositoryDynamo
    except ImportError as e:
        print(f"Error: Required modules not yet implemented: {e}")
        print("Please ensure SessionRepositoryDynamo is properly implemented.")
        return
    
    print()
    print('=' * 80)
    print('Syncing sessions from re:invent Catalog API to DynamoDB Local')
    print('=' * 80)
    print()
    
    # Create repository instance
    dynamo_repo = SessionRepositoryDynamo()
    
    print('Fetching sessions from API...')
    print('(This may take a moment as it fetches 2500+ sessions)')
    print()
    
    try:
        # Use the sync method which handles all the API fetching and data transformation
        result = dynamo_repo.sync_sessions_from_api()
        
        print()
        print('=' * 80)
        print('SYNC COMPLETED SUCCESSFULLY')
        print('=' * 80)
        print(f"  Inserted: {result['inserted']} new sessions")
        print(f"  Updated:  {result['updated']} existing sessions")
        print(f"  Total:    {result['inserted'] + result['updated']} sessions processed")
        print('=' * 80)
        print()
        
        # Verify the data
        print('Verifying data in DynamoDB...')
        all_sessions = dynamo_repo.get_all_sessions()
        print(f"✓ Total sessions in DynamoDB: {len(all_sessions)}")
        
        # Show some statistics
        if all_sessions:
            venues = set(s.venue_name for s in all_sessions)
            days = set(s.day for s in all_sessions)
            levels = set(s.level_value for s in all_sessions)
            session_types = set(s.session_type for s in all_sessions)
            
            print()
            print('Statistics:')
            print(f"  Unique venues: {len(venues)}")
            print(f"  Unique days: {len(days)}")
            print(f"  Unique levels: {len(levels)}")
            print(f"  Unique session types: {len(session_types)}")
            
            print()
            print('Sample sessions:')
            for i, session in enumerate(all_sessions[:5]):
                print(f"  {i+1}. {session.short_id} - {session.title[:60]}...")
                print(f"     Venue: {session.venue_name}, Day: {session.day}, Level: {session.level_value}")
        
        print()
        print('✓ Sessions successfully synced from API to DynamoDB Local!')
        
    except ConnectionError as e:
        print()
        print('=' * 80)
        print('ERROR: Failed to connect to API')
        print('=' * 80)
        print(f"  {str(e)}")
        print()
        print('Please check:')
        print('  1. Internet connection is available')
        print('  2. API endpoint is accessible: https://reinvent-planner.cloud/api/catalog')
        print('=' * 80)
        
    except Exception as e:
        print()
        print('=' * 80)
        print('ERROR: Sync failed')
        print('=' * 80)
        print(f"  {str(e)}")
        print('=' * 80)
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    dotenv.load_dotenv()
    sync_sessions_from_api_to_dynamo()
