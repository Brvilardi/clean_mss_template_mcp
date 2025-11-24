from typing import List, Dict, Optional, Tuple

from src.shared.domain.entities.session import Session
from src.shared.domain.repositories.session_repository_interface import ISessionRepository
from src.shared.environments import Environments
from src.shared.helpers.errors.usecase_errors import NoItemsFound
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.helpers.pagination.pagination_helper import PaginationHelper
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

    def get_all_sessions_paginated(
        self,
        page_size: int,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[Session], Optional[str]]:
        """
        Returns all sessions with pagination using Scan.
        
        Args:
            page_size: Maximum number of sessions to return (1-100)
            last_evaluated_key: Base64-encoded pagination token from previous request
            
        Returns:
            Tuple of (sessions list, next_page_token)
            
        Raises:
            ValueError: If page_size is invalid or pagination token is expired/malformed
        """
        # Validate page size
        pagination_helper = PaginationHelper()
        page_size = pagination_helper.validate_page_size(page_size)
        
        # Decode pagination token
        exclusive_start_key = None
        if last_evaluated_key:
            decoded = pagination_helper.decode_token(last_evaluated_key)
            exclusive_start_key = decoded
        
        # Build scan parameters
        scan_params = {
            'Limit': page_size,
            'FilterExpression': 'entity = :entity_type',
            'ExpressionAttributeValues': {
                ':entity_type': 'session'
            }
        }
        
        if exclusive_start_key:
            scan_params['ExclusiveStartKey'] = exclusive_start_key
        
        # Execute scan
        resp = self.dynamo.dynamo_table.scan(**scan_params)
        
        # Convert to entities
        sessions = []
        for item in resp.get('Items', []):
            sessions.append(SessionDynamoDTO.from_dynamo(item).to_entity())
        
        # Encode next page token if more results exist
        next_token = None
        if 'LastEvaluatedKey' in resp:
            next_token = pagination_helper.encode_token(resp['LastEvaluatedKey'])
        
        return sessions, next_token

    def search_sessions(
        self,
        day: Optional[str] = None,
        venue: Optional[str] = None,
        level: Optional[int] = None,
        keywords: Optional[str] = None,
        speaker: Optional[str] = None,
        page_size: int = 50,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[Session], Optional[str]]:
        """
        Search sessions with multiple filter criteria and pagination.
        Uses GSI queries when possible for optimal performance.
        
        Args:
            day: Filter by day (e.g., "Monday", "Tuesday")
            venue: Filter by venue name
            level: Filter by level value (100, 200, 300, 400)
            keywords: Space-separated keywords to search in title, abstract, topics, areas
            speaker: Filter by speaker name or company (case-insensitive, partial match)
            page_size: Maximum results per page (1-100, default 50)
            last_evaluated_key: Pagination token from previous request
            
        Returns:
            Tuple of (sessions list, next_page_token)
            
        Raises:
            ValueError: If parameters are invalid
        """
        from boto3.dynamodb.conditions import Key, Attr
        
        # Validate page size
        pagination_helper = PaginationHelper()
        page_size = pagination_helper.validate_page_size(page_size)
        
        # Decode pagination token
        exclusive_start_key = None
        offset = 0
        if last_evaluated_key:
            try:
                decoded = pagination_helper.decode_token(last_evaluated_key)
                # Check if this is an offset-based token or a DynamoDB key
                if 'offset' in decoded:
                    offset = decoded['offset']
                else:
                    exclusive_start_key = decoded
            except ValueError:
                raise ValueError("Invalid or expired pagination token")
        
        # Build speaker filter expression if provided
        speaker_filter = None
        if speaker is not None and speaker.strip():
            speaker_filter = self._build_speaker_filter_expression(speaker.strip())
        
        # Determine query strategy based on available filters
        # Priority: Level > Venue > Day (based on selectivity)
        # Note: When using offset-based pagination, we need to fetch all results
        sessions = []
        last_evaluated_key_from_db = None
        fetch_limit = page_size * 2 if offset == 0 else 1000  # Fetch more when using offset
        
        if level is not None:
            # Use GSI-Level (most selective)
            sessions, last_evaluated_key_from_db = self._query_with_gsi(
                index_name="GSI-Level",
                key_name="level_value",
                key_value=level,
                page_size=fetch_limit,
                exclusive_start_key=exclusive_start_key,
                filter_expression=speaker_filter
            )
            # Apply additional filters in application
            if day is not None:
                sessions = [s for s in sessions if s.day == day]
            if venue is not None:
                sessions = [s for s in sessions if s.venue_name == venue]
                
        elif venue is not None:
            # Use GSI-Venue (medium selectivity)
            sessions, last_evaluated_key_from_db = self._query_with_gsi(
                index_name="GSI-Venue",
                key_name="venue_name",
                key_value=venue,
                page_size=fetch_limit,
                exclusive_start_key=exclusive_start_key,
                filter_expression=speaker_filter
            )
            # Apply additional filters in application
            if day is not None:
                sessions = [s for s in sessions if s.day == day]
                
        elif day is not None:
            # Use GSI-Day (least selective of indexed filters)
            sessions, last_evaluated_key_from_db = self._query_with_gsi(
                index_name="GSI-Day",
                key_name="day",
                key_value=day,
                page_size=fetch_limit,
                exclusive_start_key=exclusive_start_key,
                filter_expression=speaker_filter
            )
            
        else:
            # No indexed filters - scan all sessions (speaker/keywords filtering in application)
            # Note: _scan_all_sessions will fetch ALL sessions from the table since we need to
            # filter by speaker/keywords in application code
            sessions, last_evaluated_key_from_db = self._scan_all_sessions(
                page_size=fetch_limit,
                exclusive_start_key=None,  # Always start from beginning for full scan
                filter_expression=speaker_filter
            )
        
        # Apply speaker filtering in application code (DynamoDB FilterExpression can't handle nested lists)
        if speaker is not None and speaker.strip():
            speaker_query_lower = speaker.strip().lower()
            sessions = [
                s for s in sessions
                if self._session_matches_speaker(s, speaker_query_lower)
            ]
        
        # Apply keyword filtering with relevance scoring
        if keywords is not None and keywords.strip():
            keyword_list = keywords.lower().split()
            sessions_with_scores = []
            
            for session in sessions:
                score = self._calculate_relevance_score(session, keyword_list)
                if score > 0:
                    sessions_with_scores.append((session, score))
            
            # Sort by relevance score (descending), then by start_datetime (ascending)
            sessions_with_scores.sort(key=lambda x: (-x[1], x[0].start_datetime))
            filtered_sessions = [s[0] for s in sessions_with_scores]
        else:
            # No keyword search - sort by start_datetime only
            filtered_sessions = sorted(sessions, key=lambda s: s.start_datetime)
        
        # Apply offset if using offset-based pagination
        if offset > 0:
            filtered_sessions = filtered_sessions[offset:]
        
        # Apply pagination to filtered results
        page_sessions = filtered_sessions[:page_size]
        
        # Generate next token if more results exist
        # Note: This is a simplified pagination approach. When we apply application-level
        # filtering (keywords, additional filters, sorting), we lose the ability to use
        # DynamoDB's native pagination efficiently. A production implementation would need
        # a more sophisticated approach, such as:
        # 1. Fetching all results and paginating in-memory (works for small datasets)
        # 2. Using a cursor-based pagination with session_id
        # 3. Storing filter state in the pagination token
        #
        # For this implementation, we'll use approach #1 since we have a small dataset
        next_token = None
        if len(filtered_sessions) > page_size:
            # We have more filtered results than requested
            # Create a simple offset-based token
            offset_token = {'offset': offset + page_size}
            next_token = pagination_helper.encode_token(offset_token)
        elif last_evaluated_key_from_db is not None and len(filtered_sessions) == len(sessions) and offset == 0:
            # DynamoDB has more results and we didn't filter anything out
            next_token = pagination_helper.encode_token(last_evaluated_key_from_db)
        
        return page_sessions, next_token
    
    def _query_with_gsi(
        self,
        index_name: str,
        key_name: str,
        key_value: any,
        page_size: int,
        exclusive_start_key: Optional[Dict] = None,
        filter_expression = None
    ) -> Tuple[List[Session], Optional[Dict]]:
        """
        Query a GSI and return matching sessions with pagination info.
        
        Args:
            index_name: Name of the GSI to query
            key_name: Partition key name for the GSI
            key_value: Value to query for
            page_size: Maximum number of items to fetch
            exclusive_start_key: Starting point for pagination
            filter_expression: Optional DynamoDB FilterExpression to apply
            
        Returns:
            Tuple of (List of Session entities, LastEvaluatedKey or None)
        """
        from boto3.dynamodb.conditions import Key
        
        query_params = {
            'IndexName': index_name,
            'KeyConditionExpression': Key(key_name).eq(key_value),
            'Limit': page_size * 2  # Fetch more to account for potential filtering
        }
        
        if exclusive_start_key:
            query_params['ExclusiveStartKey'] = exclusive_start_key
        
        if filter_expression is not None:
            query_params['FilterExpression'] = filter_expression
        
        resp = self.dynamo.dynamo_table.query(**query_params)
        
        sessions = []
        for item in resp.get('Items', []):
            sessions.append(SessionDynamoDTO.from_dynamo(item).to_entity())
        
        last_evaluated_key = resp.get('LastEvaluatedKey')
        return sessions, last_evaluated_key
    
    def _scan_all_sessions(
        self,
        page_size: int,
        exclusive_start_key: Optional[Dict] = None,
        filter_expression = None
    ) -> Tuple[List[Session], Optional[Dict]]:
        """
        Scan all sessions with entity filter and optional additional filters.
        
        When speaker or keywords are the only filters, we need to scan the entire table
        because DynamoDB can't filter nested structures efficiently. This method will
        continue scanning until it retrieves all sessions from the table.
        
        Args:
            page_size: Maximum number of items to fetch per scan operation
            exclusive_start_key: Starting point for pagination (not used in full scan)
            filter_expression: Optional DynamoDB FilterExpression to apply
            
        Returns:
            Tuple of (List of Session entities, None for last_evaluated_key since we scan all)
        """
        from boto3.dynamodb.conditions import Attr
        
        # Start with entity filter
        entity_filter = Attr('entity').eq('session')
        
        # Combine with additional filter if provided
        if filter_expression is not None:
            combined_filter = entity_filter & filter_expression
        else:
            combined_filter = entity_filter
        
        # Scan all sessions from the table
        sessions = []
        last_evaluated_key = exclusive_start_key
        
        # Keep scanning until we've retrieved all sessions
        while True:
            scan_params = {
                'FilterExpression': combined_filter
            }
            
            if last_evaluated_key:
                scan_params['ExclusiveStartKey'] = last_evaluated_key
            
            resp = self.dynamo.dynamo_table.scan(**scan_params)
            
            # Convert items to sessions
            for item in resp.get('Items', []):
                sessions.append(SessionDynamoDTO.from_dynamo(item).to_entity())
            
            # Check if there are more items to scan
            last_evaluated_key = resp.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break
        
        # Return all sessions with None for pagination key
        # (pagination will be handled in application code after filtering)
        return sessions, None
    
    def _calculate_relevance_score(self, session: Session, keywords: List[str]) -> int:
        """
        Calculate relevance score for a session based on keyword matches.
        Higher score = more relevant.
        
        Args:
            session: Session entity to score
            keywords: List of lowercase keywords to search for
            
        Returns:
            Relevance score (0 if no matches)
        """
        score = 0
        
        for keyword in keywords:
            # Title matches (highest priority)
            if keyword in session.title.lower():
                score += 10
            
            # Abstract matches
            if keyword in session.abstract.lower():
                score += 5
            
            # Topic matches
            for topic in session.topics:
                if keyword in topic.lower():
                    score += 3
                    break
            
            # Area of interest matches
            for area in session.areas_of_interest:
                if keyword in area.lower():
                    score += 2
                    break
        
        return score
    
    def _build_speaker_filter_expression(self, speaker_query: str):
        """
        Build DynamoDB filter expression for speaker search.
        
        Note: DynamoDB's FilterExpression has limitations with nested list structures.
        The contains() function doesn't support searching within list items' nested fields.
        Therefore, we return None here and handle speaker filtering in application code
        after fetching results from DynamoDB.
        
        Args:
            speaker_query: Search term for speaker name or company
            
        Returns:
            None (speaker filtering must be done in application code)
        """
        # DynamoDB FilterExpression cannot efficiently search within nested list structures
        # like speakers[*].displayName or speakers[*].company
        # We must filter in application code after fetching from DynamoDB
        return None
    
    def _session_matches_speaker(self, session: Session, speaker_query_lower: str) -> bool:
        """
        Check if a session matches the speaker query (case-insensitive partial match).
        Searches both displayName and company fields for all speakers.
        
        Args:
            session: Session entity to check
            speaker_query_lower: Lowercase speaker search query
            
        Returns:
            True if any speaker's displayName or company contains the query
        """
        for speaker in session.speakers:
            # Check displayName (case-insensitive partial match)
            display_name = speaker.get('displayName', '')
            if display_name and speaker_query_lower in display_name.lower():
                return True
            
            # Check company (case-insensitive partial match)
            company = speaker.get('company', '')
            if company and speaker_query_lower in company.lower():
                return True
        
        return False
