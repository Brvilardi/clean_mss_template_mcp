import pytest
import os
import sqlite3
import tempfile
from unittest.mock import patch, MagicMock

from src.shared.domain.entities.session import Session
from src.shared.helpers.errors.usecase_errors import NoItemsFound
from src.shared.infra.repositories.session_repository_sqlite import SessionRepositorySQLite


class TestSessionRepositorySQLite:
    """Tests for SessionRepositorySQLite."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_sessions.db")
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)
    
    @pytest.fixture
    def mock_api_response(self):
        """Mock API response with sample session data."""
        return [
            {
                'id': 'session123',
                'shortId': 'TNC301',
                'title': 'Test Session 1',
                'abstract': 'This is a test session',
                'startDateTime': '2025-12-04T21:00:00.000Z',
                'endDateTime': '2025-12-05T01:00:00.000Z',
                'day': 'Thursday',
                'speakers': [
                    {'displayName': 'John Doe', 'company': 'AWS'}
                ],
                'venueRoomName': 'Room A',
                'venue': {'displayName': 'Mandalay Bay'},
                'type': {'displayName': 'Bootcamp'},
                'level': {'displayName': '300 – Advanced', 'value': 300},
                'topics': [{'displayName': 'AI'}],
                'areaOfInterest': [{'displayName': 'Training'}],
                'features': [{'displayName': 'Hands-on'}],
                'seatCapacity': 100
            },
            {
                'id': 'session456',
                'shortId': 'TNC302',
                'title': 'Test Session 2',
                'abstract': 'Another test session',
                'startDateTime': '2025-12-05T21:00:00.000Z',
                'endDateTime': '2025-12-06T01:00:00.000Z',
                'day': 'Friday',
                'speakers': [
                    {'displayName': 'Jane Smith', 'company': 'AWS'}
                ],
                'venueRoomName': 'Room B',
                'venue': {'displayName': 'Venetian'},
                'type': {'displayName': 'Workshop'},
                'level': {'displayName': '200 – Intermediate', 'value': 200},
                'topics': [{'displayName': 'ML'}],
                'areaOfInterest': [{'displayName': 'Development'}],
                'features': [{'displayName': 'Interactive'}],
                'seatCapacity': 50
            }
        ]
    
    @pytest.fixture
    def repo_with_temp_db(self, temp_db_path, mock_api_response):
        """Create a repository instance with a temporary database."""
        with patch.object(SessionRepositorySQLite, 'DB_PATH', temp_db_path):
            with patch('src.shared.infra.repositories.session_repository_sqlite.ReinventCatalogClient') as mock_client:
                mock_client.return_value.fetch_sessions.return_value = mock_api_response
                repo = SessionRepositorySQLite()
                yield repo
    
    def test_database_creation_and_schema_initialization(self, temp_db_path):
        """Test that database and schema are created correctly."""
        with patch.object(SessionRepositorySQLite, 'DB_PATH', temp_db_path):
            with patch('src.shared.infra.repositories.session_repository_sqlite.ReinventCatalogClient') as mock_client:
                mock_client.return_value.fetch_sessions.return_value = []
                
                repo = SessionRepositorySQLite()
                
                # Verify database file exists
                assert os.path.exists(temp_db_path)
                
                # Verify table exists
                conn = sqlite3.connect(temp_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
                table = cursor.fetchone()
                conn.close()
                
                assert table is not None
                assert table[0] == 'sessions'
    
    def test_get_all_sessions_empty_database(self, temp_db_path):
        """Test get_all_sessions returns empty list when database is empty."""
        with patch.object(SessionRepositorySQLite, 'DB_PATH', temp_db_path):
            with patch('src.shared.infra.repositories.session_repository_sqlite.ReinventCatalogClient') as mock_client:
                mock_client.return_value.fetch_sessions.return_value = []
                
                repo = SessionRepositorySQLite()
                sessions = repo.get_all_sessions()
                
                assert sessions == []
    
    def test_get_all_sessions_populated_database(self, repo_with_temp_db):
        """Test get_all_sessions returns all sessions from database."""
        sessions = repo_with_temp_db.get_all_sessions()
        
        assert len(sessions) == 2
        assert all(isinstance(session, Session) for session in sessions)
        assert sessions[0].session_id == 'session123'
        assert sessions[0].title == 'Test Session 1'
        assert sessions[1].session_id == 'session456'
        assert sessions[1].title == 'Test Session 2'
    
    def test_get_session_by_id_valid(self, repo_with_temp_db):
        """Test get_session_by_id returns correct session."""
        session = repo_with_temp_db.get_session_by_id('session123')
        
        assert isinstance(session, Session)
        assert session.session_id == 'session123'
        assert session.short_id == 'TNC301'
        assert session.title == 'Test Session 1'
        assert session.session_type == 'Bootcamp'
        assert session.level_value == 300
    
    def test_get_session_by_id_not_found(self, repo_with_temp_db):
        """Test get_session_by_id raises NoItemsFound for invalid ID."""
        with pytest.raises(NoItemsFound):
            repo_with_temp_db.get_session_by_id('nonexistent')
    
    def test_sync_sessions_from_api(self, temp_db_path, mock_api_response):
        """Test sync_sessions_from_api fetches and stores sessions."""
        with patch.object(SessionRepositorySQLite, 'DB_PATH', temp_db_path):
            with patch('src.shared.infra.repositories.session_repository_sqlite.ReinventCatalogClient') as mock_client:
                # First initialization with empty response
                mock_client.return_value.fetch_sessions.return_value = []
                repo = SessionRepositorySQLite()
                
                # Now sync with actual data
                mock_client.return_value.fetch_sessions.return_value = mock_api_response
                result = repo.sync_sessions_from_api()
                
                assert result['inserted'] == 2
                assert result['updated'] == 0
                
                # Verify sessions are in database
                sessions = repo.get_all_sessions()
                assert len(sessions) == 2
    
    def test_sync_sessions_from_api_updates_existing(self, repo_with_temp_db, mock_api_response):
        """Test sync_sessions_from_api updates existing sessions."""
        # Modify the mock data
        modified_data = mock_api_response.copy()
        modified_data[0]['title'] = 'Updated Test Session 1'
        
        with patch('src.shared.infra.repositories.session_repository_sqlite.ReinventCatalogClient') as mock_client:
            mock_client.return_value.fetch_sessions.return_value = modified_data
            
            result = repo_with_temp_db.sync_sessions_from_api()
            
            assert result['inserted'] == 0
            assert result['updated'] == 2
            
            # Verify update
            session = repo_with_temp_db.get_session_by_id('session123')
            assert session.title == 'Updated Test Session 1'
    
    def test_sync_sessions_from_api_connection_error(self, temp_db_path):
        """Test sync_sessions_from_api raises ConnectionError when API fails."""
        with patch.object(SessionRepositorySQLite, 'DB_PATH', temp_db_path):
            with patch('src.shared.infra.repositories.session_repository_sqlite.ReinventCatalogClient') as mock_client:
                # Initialize with empty database first
                mock_client.return_value.fetch_sessions.return_value = []
                repo = SessionRepositorySQLite()
                
                # Now test that sync raises ConnectionError
                mock_client.return_value.fetch_sessions.side_effect = ConnectionError("API unreachable")
                
                with pytest.raises(ConnectionError):
                    repo.sync_sessions_from_api()
    
    def test_auto_populate_on_initialization(self, temp_db_path, mock_api_response):
        """Test that database is auto-populated when empty on initialization."""
        with patch.object(SessionRepositorySQLite, 'DB_PATH', temp_db_path):
            with patch('src.shared.infra.repositories.session_repository_sqlite.ReinventCatalogClient') as mock_client:
                mock_client.return_value.fetch_sessions.return_value = mock_api_response
                
                repo = SessionRepositorySQLite()
                
                # Verify sessions were auto-populated
                sessions = repo.get_all_sessions()
                assert len(sessions) == 2
    
    def test_transaction_rollback_on_error(self, temp_db_path):
        """Test that transaction is rolled back on error during sync."""
        with patch.object(SessionRepositorySQLite, 'DB_PATH', temp_db_path):
            with patch('src.shared.infra.repositories.session_repository_sqlite.ReinventCatalogClient') as mock_client:
                # Initialize with empty database
                mock_client.return_value.fetch_sessions.return_value = []
                repo = SessionRepositorySQLite()
                
                # Create invalid data that will cause an error during processing
                invalid_data = [
                    {
                        'id': 'valid123',
                        'shortId': 'TNC301',
                        'title': 'Valid Session',
                        'abstract': 'Valid',
                        'startDateTime': '2025-12-04T21:00:00.000Z',
                        'endDateTime': '2025-12-05T01:00:00.000Z',
                        'day': 'Thursday',
                        'speakers': [],
                        'venueRoomName': 'Room A',
                        'venue': {'displayName': 'Venue'},
                        'type': {'displayName': 'Type'},
                        'level': {'displayName': '300', 'value': 300},
                        'topics': [],
                        'areaOfInterest': [],
                        'features': [],
                        'seatCapacity': 100
                    },
                    {
                        'id': 'invalid',
                        'shortId': 'BAD',
                        'title': 'X',  # Too short, will fail validation
                        'abstract': 'Invalid',
                        'startDateTime': '2025-12-04T21:00:00.000Z',
                        'endDateTime': '2025-12-05T01:00:00.000Z',
                        'day': 'Thursday',
                        'speakers': [],
                        'venueRoomName': 'Room B',
                        'venue': {'displayName': 'Venue'},
                        'type': {'displayName': 'Type'},
                        'level': {'displayName': '200', 'value': 200},
                        'topics': [],
                        'areaOfInterest': [],
                        'features': [],
                        'seatCapacity': 50
                    }
                ]
                
                mock_client.return_value.fetch_sessions.return_value = invalid_data
                
                # Sync should skip invalid session but continue
                result = repo.sync_sessions_from_api()
                
                # Only valid session should be inserted
                assert result['inserted'] == 1
                sessions = repo.get_all_sessions()
                assert len(sessions) == 1
                assert sessions[0].session_id == 'valid123'
