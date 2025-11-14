from src.shared.domain.entities.session import Session
from src.shared.helpers.errors.usecase_errors import NoItemsFound
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock
import pytest


class Test_SessionRepositoryMock:
    def test_get_session_by_id(self):
        """Test retrieving a session by ID"""
        repo = SessionRepositoryMock()
        session = repo.get_session_by_id("1753651605588001kjXl")
        
        assert session.session_id == "1753651605588001kjXl"
        assert session.short_id == "TNC301"
        assert session.title == "Accelerate VMware Migration with AWS Transform"
    
    def test_get_session_by_id_not_found(self):
        """Test retrieving non-existent session raises NoItemsFound"""
        repo = SessionRepositoryMock()
        with pytest.raises(NoItemsFound):
            repo.get_session_by_id("nonexistent_id")
    
    def test_get_all_sessions(self):
        """Test retrieving all sessions"""
        repo = SessionRepositoryMock()
        sessions = repo.get_all_sessions()
        assert len(sessions) == 5
    
    def test_sync_sessions_from_api(self):
        """Test syncing sessions from API inserts new session"""
        repo = SessionRepositoryMock()
        initial_count = len(repo.sessions)
        
        result = repo.sync_sessions_from_api()
        
        assert result["inserted"] == 1
        assert result["updated"] == 0
        assert len(repo.sessions) == initial_count + 1
        
        # Verify the new session was added
        new_session = repo.get_session_by_id("1753651605588006qrST")
        assert new_session.short_id == "AI303"
        assert new_session.title == "Generative AI Applications with Amazon Bedrock"
        assert new_session.venue_name == "Venetian"
        assert new_session.level_value == 300
    
    def test_sync_sessions_from_api_idempotent(self):
        """Test syncing sessions from API is idempotent (doesn't duplicate)"""
        repo = SessionRepositoryMock()
        
        # First sync
        result1 = repo.sync_sessions_from_api()
        assert result1["inserted"] == 1
        assert result1["updated"] == 0
        count_after_first = len(repo.sessions)
        
        # Second sync - should not insert duplicate
        result2 = repo.sync_sessions_from_api()
        assert result2["inserted"] == 0
        assert result2["updated"] == 0
        assert len(repo.sessions) == count_after_first
    
    def test_sync_sessions_from_api_returns_correct_counts(self):
        """Test sync_sessions_from_api returns correct inserted and updated counts"""
        repo = SessionRepositoryMock()
        
        result = repo.sync_sessions_from_api()
        
        # Verify return structure
        assert "inserted" in result
        assert "updated" in result
        assert isinstance(result["inserted"], int)
        assert isinstance(result["updated"], int)
        assert result["inserted"] >= 0
        assert result["updated"] >= 0
    
    def test_get_sessions_by_venue(self):
        """Test retrieving sessions filtered by venue"""
        repo = SessionRepositoryMock()
        sessions = repo.get_sessions_by_venue("Venetian")
        
        assert len(sessions) == 1
        assert sessions[0].venue_name == "Venetian"
        assert sessions[0].short_id == "SVS201"
    
    def test_get_sessions_by_venue_multiple_results(self):
        """Test retrieving multiple sessions from same venue ordered by start_datetime"""
        repo = SessionRepositoryMock()
        
        # Add another Venetian session with earlier start time
        early_session = Session(
            session_id="test_early_venetian",
            short_id="VEN100",
            title="Early Venetian Session",
            abstract="Test session",
            session_type="Breakout Session",
            venue_name="Venetian",
            venue_room="Test Room",
            start_datetime="2025-12-05T08:00:00.000Z",
            end_datetime="2025-12-05T09:00:00.000Z",
            day="Friday",
            speakers=[{"displayName": "Test Speaker", "company": "AWS"}],
            topics=["Test"],
            areas_of_interest=["Test"],
            level="100 – Foundational",
            level_value=100,
            features=[],
            seat_capacity=50
        )
        repo.sessions.append(early_session)
        
        sessions = repo.get_sessions_by_venue("Venetian")
        
        assert len(sessions) == 2
        assert sessions[0].start_datetime == "2025-12-05T08:00:00.000Z"
        assert sessions[1].start_datetime == "2025-12-05T14:00:00.000Z"
    
    def test_get_sessions_by_venue_empty_result(self):
        """Test retrieving sessions from non-existent venue"""
        repo = SessionRepositoryMock()
        sessions = repo.get_sessions_by_venue("NonExistentVenue")
        
        assert len(sessions) == 0
        assert sessions == []
    
    def test_get_sessions_by_day(self):
        """Test retrieving sessions filtered by day"""
        repo = SessionRepositoryMock()
        sessions = repo.get_sessions_by_day("Friday")
        
        assert len(sessions) == 2
        assert all(s.day == "Friday" for s in sessions)
        # Verify ordering by start_datetime
        assert sessions[0].start_datetime == "2025-12-05T10:30:00.000Z"
        assert sessions[1].start_datetime == "2025-12-05T14:00:00.000Z"
    
    def test_get_sessions_by_day_single_result(self):
        """Test retrieving sessions for day with single session"""
        repo = SessionRepositoryMock()
        sessions = repo.get_sessions_by_day("Thursday")
        
        assert len(sessions) == 1
        assert sessions[0].day == "Thursday"
        assert sessions[0].short_id == "TNC301"
    
    def test_get_sessions_by_day_empty_result(self):
        """Test retrieving sessions for day with no sessions"""
        repo = SessionRepositoryMock()
        sessions = repo.get_sessions_by_day("Monday")
        
        assert len(sessions) == 0
        assert sessions == []
    
    def test_get_sessions_by_level(self):
        """Test retrieving sessions filtered by level value"""
        repo = SessionRepositoryMock()
        sessions = repo.get_sessions_by_level(200)
        
        assert len(sessions) == 2
        assert all(s.level_value == 200 for s in sessions)
        # Verify ordering by start_datetime
        assert sessions[0].start_datetime == "2025-12-05T10:30:00.000Z"
        assert sessions[1].start_datetime == "2025-12-05T14:00:00.000Z"
    
    def test_get_sessions_by_level_single_result(self):
        """Test retrieving sessions for level with single session"""
        repo = SessionRepositoryMock()
        sessions = repo.get_sessions_by_level(100)
        
        assert len(sessions) == 1
        assert sessions[0].level_value == 100
        assert sessions[0].short_id == "SEC101"
    
    def test_get_sessions_by_level_empty_result(self):
        """Test retrieving sessions for level with no sessions"""
        repo = SessionRepositoryMock()
        # Remove all level 400 sessions first
        repo.sessions = [s for s in repo.sessions if s.level_value != 400]
        sessions = repo.get_sessions_by_level(400)
        
        assert len(sessions) == 0
        assert sessions == []
    
    def test_get_sessions_by_level_ordering(self):
        """Test that sessions are properly ordered by start_datetime"""
        repo = SessionRepositoryMock()
        
        # Add sessions with same level but different times
        session1 = Session(
            session_id="test_level_late",
            short_id="LVL301",
            title="Late Level 300 Session",
            abstract="Test session",
            session_type="Breakout Session",
            venue_name="Test Venue",
            venue_room="Test Room",
            start_datetime="2025-12-08T20:00:00.000Z",
            end_datetime="2025-12-08T21:00:00.000Z",
            day="Monday",
            speakers=[{"displayName": "Test Speaker", "company": "AWS"}],
            topics=["Test"],
            areas_of_interest=["Test"],
            level="300 – Advanced",
            level_value=300,
            features=[],
            seat_capacity=50
        )
        
        session2 = Session(
            session_id="test_level_early",
            short_id="LVL302",
            title="Early Level 300 Session",
            abstract="Test session",
            session_type="Breakout Session",
            venue_name="Test Venue",
            venue_room="Test Room",
            start_datetime="2025-12-04T08:00:00.000Z",
            end_datetime="2025-12-04T09:00:00.000Z",
            day="Thursday",
            speakers=[{"displayName": "Test Speaker", "company": "AWS"}],
            topics=["Test"],
            areas_of_interest=["Test"],
            level="300 – Advanced",
            level_value=300,
            features=[],
            seat_capacity=50
        )
        
        repo.sessions.extend([session1, session2])
        
        sessions = repo.get_sessions_by_level(300)
        
        assert len(sessions) == 3
        # Verify chronological ordering
        assert sessions[0].start_datetime == "2025-12-04T08:00:00.000Z"
        assert sessions[1].start_datetime == "2025-12-04T21:00:00.000Z"
        assert sessions[2].start_datetime == "2025-12-08T20:00:00.000Z"
