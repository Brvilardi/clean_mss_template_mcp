from typing import List, Dict, Optional, Tuple

from src.shared.domain.entities.session import Session
from src.shared.domain.repositories.session_repository_interface import ISessionRepository
from src.shared.helpers.errors.usecase_errors import NoItemsFound
from src.shared.helpers.pagination.pagination_helper import PaginationHelper


class SessionRepositoryMock(ISessionRepository):
    """
    Mock implementation of ISessionRepository for testing purposes.
    Pre-populated with sample re:invent sessions covering different types.
    """

    def __init__(self):
        self.sessions: List[Session] = []
        self._populate_sample_data()

    def _populate_sample_data(self):
        """Pre-populate repository with sample re:invent sessions."""
        sample_sessions = [
            Session(
                session_id="1753651605588001kjXl",
                short_id="TNC301",
                title="Accelerate VMware Migration with AWS Transform",
                abstract="This bootcamp is for AWS Partners only. Learn how to accelerate VMware migration using AWS Transform services and best practices.",
                session_type="Bootcamp",
                venue_name="Mandalay Bay",
                venue_room="Level 2 South | Breakers K",
                start_datetime="2025-12-04T21:00:00.000Z",
                end_datetime="2025-12-05T01:00:00.000Z",
                day="Thursday",
                speakers=[
                    {"displayName": "Parvesh Chopra", "company": "AWS"}
                ],
                topics=["Artificial Intelligence", "Migration"],
                areas_of_interest=["Training & Certification"],
                level="300 – Advanced",
                level_value=300,
                features=["Hands-on"],
                seat_capacity=126
            ),
            Session(
                session_id="1753651605588002abCD",
                short_id="SVS201",
                title="Building Serverless Applications with AWS Lambda",
                abstract="Learn the fundamentals of building serverless applications using AWS Lambda, API Gateway, and DynamoDB.",
                session_type="Breakout Session",
                venue_name="Venetian",
                venue_room="Level 3 | Marcello 4405",
                start_datetime="2025-12-05T14:00:00.000Z",
                end_datetime="2025-12-05T15:00:00.000Z",
                day="Friday",
                speakers=[
                    {"displayName": "Jane Smith", "company": "AWS"},
                    {"displayName": "John Doe", "company": "AWS"}
                ],
                topics=["Serverless", "Compute"],
                areas_of_interest=["Application Development"],
                level="200 – Intermediate",
                level_value=200,
                features=["Interactive"],
                seat_capacity=250
            ),
            Session(
                session_id="1753651605588003efGH",
                short_id="SEC101",
                title="Introduction to AWS Security Best Practices",
                abstract="Get started with AWS security fundamentals. Learn about IAM, encryption, network security, and compliance.",
                session_type="Workshop",
                venue_name="MGM Grand",
                venue_room="Level 1 | Grand Ballroom A",
                start_datetime="2025-12-06T09:00:00.000Z",
                end_datetime="2025-12-06T12:00:00.000Z",
                day="Saturday",
                speakers=[
                    {"displayName": "Alice Johnson", "company": "AWS"}
                ],
                topics=["Security", "Identity & Access Management"],
                areas_of_interest=["Security & Compliance"],
                level="100 – Foundational",
                level_value=100,
                features=["Hands-on", "Interactive"],
                seat_capacity=100
            ),
            Session(
                session_id="1753651605588004ijKL",
                short_id="DAT401",
                title="Advanced Data Analytics with Amazon Redshift",
                abstract="Deep dive into advanced analytics patterns using Amazon Redshift. Learn about performance optimization, data modeling, and integration with ML services.",
                session_type="Chalk Talk",
                venue_name="Wynn",
                venue_room="Level 2 | Lafite 1",
                start_datetime="2025-12-07T16:00:00.000Z",
                end_datetime="2025-12-07T17:00:00.000Z",
                day="Sunday",
                speakers=[
                    {"displayName": "Bob Williams", "company": "AWS"},
                    {"displayName": "Carol Martinez", "company": "Amazon"}
                ],
                topics=["Analytics", "Data Lakes", "Machine Learning"],
                areas_of_interest=["Data & Analytics"],
                level="400 – Expert",
                level_value=400,
                features=["Interactive"],
                seat_capacity=50
            ),
            Session(
                session_id="1753651605588005mnOP",
                short_id="CON202",
                title="Container Orchestration with Amazon ECS and EKS",
                abstract="Compare and contrast Amazon ECS and EKS for container orchestration. Learn when to use each service and best practices for deployment.",
                session_type="Breakout Session",
                venue_name="Caesars Forum",
                venue_room="Level 1 | Forum 108",
                start_datetime="2025-12-05T10:30:00.000Z",
                end_datetime="2025-12-05T11:30:00.000Z",
                day="Friday",
                speakers=[
                    {"displayName": "David Chen", "company": "AWS"}
                ],
                topics=["Containers", "Kubernetes", "Compute"],
                areas_of_interest=["Application Development", "DevOps"],
                level="200 – Intermediate",
                level_value=200,
                features=[],
                seat_capacity=300
            )
        ]
        
        self.sessions = sample_sessions

    def get_all_sessions(self) -> List[Session]:
        """
        Returns all sessions from the mock repository.
        
        Returns:
            List of Session entities
        """
        return self.sessions.copy()

    def sync_sessions_from_api(self) -> Dict[str, int]:
        """
        Simulates syncing sessions from external API.
        In mock implementation, this adds one new session to demonstrate sync behavior.
        
        Returns:
            Dictionary with keys 'inserted' and 'updated' containing counts
        """
        # Simulate adding a new session during sync
        new_session = Session(
            session_id="1753651605588006qrST",
            short_id="AI303",
            title="Generative AI Applications with Amazon Bedrock",
            abstract="Explore building generative AI applications using Amazon Bedrock. Learn about foundation models, prompt engineering, and RAG patterns.",
            session_type="Workshop",
            venue_name="Venetian",
            venue_room="Level 2 | Bellini 2004",
            start_datetime="2025-12-06T13:00:00.000Z",
            end_datetime="2025-12-06T16:00:00.000Z",
            day="Saturday",
            speakers=[
                {"displayName": "Emily Rodriguez", "company": "AWS"}
            ],
            topics=["Artificial Intelligence", "Machine Learning", "Generative AI"],
            areas_of_interest=["AI & Machine Learning"],
            level="300 – Advanced",
            level_value=300,
            features=["Hands-on"],
            seat_capacity=75
        )
        
        # Check if session already exists
        existing_ids = [s.session_id for s in self.sessions]
        if new_session.session_id not in existing_ids:
            self.sessions.append(new_session)
            return {"inserted": 1, "updated": 0}
        else:
            return {"inserted": 0, "updated": 0}

    def get_session_by_id(self, session_id: str) -> Session:
        """
        Returns a specific session by ID.
        
        Args:
            session_id: The unique session identifier
            
        Returns:
            Session entity
            
        Raises:
            NoItemsFound: If session with given ID is not found
        """
        for session in self.sessions:
            if session.session_id == session_id:
                return session
        
        raise NoItemsFound(f"session_id: {session_id}")

    def get_sessions_by_venue(self, venue_name: str) -> List[Session]:
        """
        Returns sessions filtered by venue name, ordered by start_datetime.
        
        Args:
            venue_name: The venue name to filter by
            
        Returns:
            List of Session entities ordered by start_datetime
        """
        filtered_sessions = [
            session for session in self.sessions
            if session.venue_name == venue_name
        ]
        
        # Sort by start_datetime
        return sorted(filtered_sessions, key=lambda s: s.start_datetime)

    def get_sessions_by_day(self, day: str) -> List[Session]:
        """
        Returns sessions filtered by day, ordered by start_datetime.
        
        Args:
            day: The day to filter by (e.g., "Monday", "Tuesday")
            
        Returns:
            List of Session entities ordered by start_datetime
        """
        filtered_sessions = [
            session for session in self.sessions
            if session.day == day
        ]
        
        # Sort by start_datetime
        return sorted(filtered_sessions, key=lambda s: s.start_datetime)

    def get_sessions_by_level(self, level_value: int) -> List[Session]:
        """
        Returns sessions filtered by level value, ordered by start_datetime.
        
        Args:
            level_value: The level value to filter by (100, 200, 300, 400)
            
        Returns:
            List of Session entities ordered by start_datetime
        """
        filtered_sessions = [
            session for session in self.sessions
            if session.level_value == level_value
        ]
        
        # Sort by start_datetime
        return sorted(filtered_sessions, key=lambda s: s.start_datetime)

    def get_sessions_by_short_id(self, short_id: str) -> List[Session]:
        """
        Returns sessions filtered by short_id (case-insensitive).
        
        Args:
            short_id: The short ID to filter by (e.g., "TNC301")
            
        Returns:
            List of Session entities (typically 0 or 1 result)
        """
        filtered_sessions = [
            session for session in self.sessions
            if session.short_id.lower() == short_id.lower()
        ]
        
        return filtered_sessions

    def get_all_sessions_paginated(
        self,
        page_size: int,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[Session], Optional[str]]:
        """
        Returns all sessions with simulated pagination.
        
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
        
        # Decode start index from token
        start_index = 0
        if last_evaluated_key:
            decoded = pagination_helper.decode_token(last_evaluated_key)
            start_index = decoded.get('index', 0)
        
        # Slice results
        end_index = start_index + page_size
        page_sessions = self.sessions[start_index:end_index]
        
        # Generate next token if more results exist
        next_token = None
        if end_index < len(self.sessions):
            next_key = {'index': end_index}
            next_token = pagination_helper.encode_token(next_key)
        
        return page_sessions, next_token

    def search_sessions(
        self,
        day: Optional[str] = None,
        venue: Optional[str] = None,
        level: Optional[int] = None,
        keywords: Optional[str] = None,
        page_size: int = 50,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[Session], Optional[str]]:
        """
        Search sessions with multiple filter criteria and pagination.
        
        Args:
            day: Filter by day (e.g., "Monday", "Tuesday")
            venue: Filter by venue name
            level: Filter by level value (100, 200, 300, 400)
            keywords: Space-separated keywords to search in title, abstract, topics, areas
            page_size: Maximum results per page (1-100, default 50)
            last_evaluated_key: Pagination token from previous request
            
        Returns:
            Tuple of (sessions list, next_page_token)
            
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate page size
        pagination_helper = PaginationHelper()
        page_size = pagination_helper.validate_page_size(page_size)
        
        # Start with all sessions
        filtered_sessions = self.sessions.copy()
        
        # Apply indexed filters
        if day is not None:
            filtered_sessions = [s for s in filtered_sessions if s.day == day]
        
        if venue is not None:
            filtered_sessions = [s for s in filtered_sessions if s.venue_name == venue]
        
        if level is not None:
            filtered_sessions = [s for s in filtered_sessions if s.level_value == level]
        
        # Apply keyword filtering with relevance scoring
        if keywords is not None and keywords.strip():
            keyword_list = keywords.lower().split()
            sessions_with_scores = []
            
            for session in filtered_sessions:
                score = self._calculate_relevance_score(session, keyword_list)
                if score > 0:
                    sessions_with_scores.append((session, score))
            
            # Sort by relevance score (descending), then by start_datetime (ascending)
            sessions_with_scores.sort(key=lambda x: (-x[1], x[0].start_datetime))
            filtered_sessions = [s[0] for s in sessions_with_scores]
        else:
            # No keyword search - sort by start_datetime only
            filtered_sessions.sort(key=lambda s: s.start_datetime)
        
        # Apply pagination
        start_index = 0
        if last_evaluated_key:
            decoded = pagination_helper.decode_token(last_evaluated_key)
            start_index = decoded.get('index', 0)
        
        # Slice results
        end_index = start_index + page_size
        page_sessions = filtered_sessions[start_index:end_index]
        
        # Generate next token if more results exist
        next_token = None
        if end_index < len(filtered_sessions):
            next_key = {'index': end_index}
            next_token = pagination_helper.encode_token(next_key)
        
        return page_sessions, next_token
    
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
