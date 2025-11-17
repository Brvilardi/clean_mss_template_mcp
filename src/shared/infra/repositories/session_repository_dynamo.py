from typing import List, Dict

from src.shared.domain.entities.session import Session
from src.shared.domain.repositories.session_repository_interface import ISessionRepository
from src.shared.environments import Environments
from src.shared.helpers.errors.usecase_errors import NoItemsFound
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.infra.dto.session_dynamo_dto import SessionDynamoDTO
from src.shared.infra.external.dynamo.datasources.dynamo_datasource import DynamoDatasource
from src.shared.infra.external.reinvent.reinvent_catalog_client import ReinventCatalogClient


class SessionRepositoryDynamo(ISessionRepository):
    """
    DynamoDB implementation of ISessionRepository.
    Uses a table with only partition key (PK) and three GSIs for optimized queries.
    """

    @staticmethod
    def partition_key_format(session_id: str) -> str:
        """
        Format the partition key for a session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Formatted partition key: SESSION#{session_id}
        """
        return f"SESSION#{session_id}"

    def __init__(self):
        """
        Initialize the DynamoDB datasource with Sessions table configuration.
        Uses SESSIONS_DYNAMO_* environment variables for configuration.
        """
        envs = Environments.get_envs()
        
        # Get Sessions-specific environment variables
        sessions_table_name = getattr(envs, 'sessions_dynamo_table_name', envs.dynamo_table_name)
        sessions_partition_key = getattr(envs, 'sessions_dynamo_partition_key', 'PK')
        
        self.dynamo = DynamoDatasource(
            endpoint_url=envs.endpoint_url,
            dynamo_table_name=sessions_table_name,
            region=envs.region,
            partition_key=sessions_partition_key,
            sort_key=None  # Sessions table has no sort key
        )
        
        self.api_client = ReinventCatalogClient()

    def get_session_by_id(self, session_id: str) -> Session:
        """
        Returns a specific session by ID using GetItem.
        
        Args:
            session_id: The unique session identifier
            
        Returns:
            Session entity
            
        Raises:
            NoItemsFound: If session with given ID is not found
        """
        # For tables without sort key, we need to use get_item differently
        pk = self.partition_key_format(session_id)
        resp = self.dynamo.dynamo_table.get_item(Key={self.dynamo.partition_key: pk})
        
        if resp.get('Item') is None:
            raise NoItemsFound(f"session_id: {session_id}")
        
        session_dto = SessionDynamoDTO.from_dynamo(resp["Item"])
        return session_dto.to_entity()

    def get_all_sessions(self) -> List[Session]:
        """
        Returns all sessions from storage using Scan with entity filter.
        
        Returns:
            List of Session entities
        """
        resp = self.dynamo.get_all_items()
        sessions = []
        
        for item in resp['Items']:
            if item.get("entity") == 'session':
                sessions.append(SessionDynamoDTO.from_dynamo(item).to_entity())
        
        return sessions

    def sync_sessions_from_api(self) -> Dict[str, int]:
        """
        Fetches data from external API and updates storage using batch write.
        
        Returns:
            Dictionary with keys 'inserted' and 'updated' containing counts
            
        Raises:
            ConnectionError: If external API is unreachable
            EntityError: If API data is invalid
        """
        try:
            # Fetch sessions from API
            api_sessions = self.api_client.fetch_sessions()
            
            # Get existing session IDs to determine inserts vs updates
            existing_sessions = self.get_all_sessions()
            existing_ids = {session.session_id for session in existing_sessions}
            
            inserted_count = 0
            updated_count = 0
            
            # Prepare items for batch write
            items_to_write = []
            
            for api_session_data in api_sessions:
                try:
                    # Extract nested structures from API response
                    speakers = [
                        {
                            "displayName": s.get("displayName", ""),
                            "company": s.get("company", "")
                        }
                        for s in api_session_data.get("speakers", [])
                    ]
                    
                    topics = [
                        t.get("displayName", "")
                        for t in api_session_data.get("topics", [])
                    ]
                    
                    areas_of_interest = [
                        a.get("displayName", "")
                        for a in api_session_data.get("areaOfInterest", [])
                    ]
                    
                    features = [
                        f.get("displayName", "")
                        for f in api_session_data.get("features", [])
                    ]
                    
                    # Extract level information (handle None values)
                    level_data = api_session_data.get('level', {}) or {}
                    level_display = level_data.get('displayName', '') or 'Not specified'
                    level_value = level_data.get('value')
                    # Convert None to 0 for sessions without a defined level
                    if level_value is None:
                        level_value = 0
                    
                    # Create Session entity with correctly mapped fields from API
                    session = Session(
                        session_id=api_session_data.get('id', ''),
                        short_id=api_session_data.get('shortId', ''),
                        title=api_session_data.get('title', ''),
                        abstract=api_session_data.get('abstract', ''),
                        session_type=api_session_data.get('type', {}).get('displayName', ''),
                        venue_name=api_session_data.get('venue', {}).get('displayName', ''),
                        venue_room=api_session_data.get('venueRoomName', ''),
                        start_datetime=api_session_data.get('startDateTime', ''),
                        end_datetime=api_session_data.get('endDateTime', ''),
                        day=api_session_data.get('day', ''),
                        speakers=speakers,
                        topics=topics,
                        areas_of_interest=areas_of_interest,
                        level=level_display,
                        level_value=level_value,
                        features=features,
                        seat_capacity=api_session_data.get('seatCapacity', 0)
                    )
                    
                    # Convert to DTO and prepare for DynamoDB
                    session_dto = SessionDynamoDTO.from_entity(session)
                    dynamo_item = session_dto.to_dynamo()
                    
                    # Add partition key
                    dynamo_item[self.dynamo.partition_key] = self.partition_key_format(session.session_id)
                    
                    items_to_write.append(dynamo_item)
                    
                    # Track if insert or update
                    if session.session_id in existing_ids:
                        updated_count += 1
                    else:
                        inserted_count += 1
                        
                except EntityError as e:
                    # Log and skip invalid sessions
                    print(f"Skipping invalid session data: {e}")
                    continue
            
            # Batch write items (DynamoDB batch_write_items handles up to 25 items per batch automatically)
            if items_to_write:
                self.dynamo.batch_write_items(items_to_write)
            
            return {
                "inserted": inserted_count,
                "updated": updated_count
            }
            
        except ConnectionError as e:
            # Re-raise connection errors
            raise e
        except Exception as e:
            # Wrap other errors as EntityError
            raise EntityError(f"Failed to sync sessions from API: {str(e)}")

    def get_sessions_by_venue(self, venue_name: str) -> List[Session]:
        """
        Returns sessions filtered by venue name using GSI-Venue, ordered by start_datetime.
        
        Args:
            venue_name: The venue name to filter by
            
        Returns:
            List of Session entities ordered by start_datetime
        """
        from boto3.dynamodb.conditions import Key
        
        resp = self.dynamo.query(
            key_condition_expression=Key('venue_name').eq(venue_name),
            IndexName="GSI-Venue"
        )
        
        sessions = []
        for item in resp.get('Items', []):
            sessions.append(SessionDynamoDTO.from_dynamo(item).to_entity())
        
        # Results are already ordered by start_datetime (GSI sort key)
        return sessions

    def get_sessions_by_day(self, day: str) -> List[Session]:
        """
        Returns sessions filtered by day using GSI-Day, ordered by start_datetime.
        
        Args:
            day: The day to filter by (e.g., "Monday", "Tuesday")
            
        Returns:
            List of Session entities ordered by start_datetime
        """
        from boto3.dynamodb.conditions import Key
        
        resp = self.dynamo.query(
            key_condition_expression=Key('day').eq(day),
            IndexName="GSI-Day"
        )
        
        sessions = []
        for item in resp.get('Items', []):
            sessions.append(SessionDynamoDTO.from_dynamo(item).to_entity())
        
        # Results are already ordered by start_datetime (GSI sort key)
        return sessions

    def get_sessions_by_level(self, level_value: int) -> List[Session]:
        """
        Returns sessions filtered by level value using GSI-Level, ordered by start_datetime.
        
        Args:
            level_value: The level value to filter by (100, 200, 300, 400)
            
        Returns:
            List of Session entities ordered by start_datetime
        """
        from boto3.dynamodb.conditions import Key
        
        resp = self.dynamo.query(
            key_condition_expression=Key('level_value').eq(level_value),
            IndexName="GSI-Level"
        )
        
        sessions = []
        for item in resp.get('Items', []):
            sessions.append(SessionDynamoDTO.from_dynamo(item).to_entity())
        
        # Results are already ordered by start_datetime (GSI sort key)
        return sessions

    def get_sessions_by_short_id(self, short_id: str) -> List[Session]:
        """
        Returns sessions filtered by short_id (case-insensitive).
        Note: Without a GSI for short_id, this performs a scan with filter.
        
        Args:
            short_id: The short ID to filter by (e.g., "TNC301")
            
        Returns:
            List of Session entities (typically 0 or 1 result)
        """
        from boto3.dynamodb.conditions import Attr
        
        # Scan with filter expression for short_id (case-insensitive)
        # Note: DynamoDB doesn't support case-insensitive comparisons natively,
        # so we need to filter in application code
        all_sessions = self.get_all_sessions()
        
        # Filter by short_id (case-insensitive)
        filtered_sessions = [
            session for session in all_sessions
            if session.short_id.lower() == short_id.lower()
        ]
        
        return filtered_sessions
