import os
import pytest
import boto3

from src.shared.infra.repositories.session_repository_dynamo import SessionRepositoryDynamo
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock
from src.shared.infra.dto.session_dynamo_dto import SessionDynamoDTO
from src.shared.helpers.errors.usecase_errors import NoItemsFound


class Test_SessionRepositoryDynamo:
    """
    Tests for SessionRepositoryDynamo with DynamoDB Local.
    
    Prerequisites:
    1. DynamoDB Local running on http://localhost:8000
    2. Tests automatically clear and reload mock data before each test
    """
    
    @pytest.fixture(autouse=True)
    def setup_dynamodb_local(self):
        """
        Setup fixture that runs before each test.
        Ensures TEST environment and clears/reloads DynamoDB Local with mock data.
        """
        # Set environment to TEST (uses DynamoDB Local)
        os.environ["ENDPOINT_URL"] = "http://localhost:8000"
        
        # Clear all items from DynamoDB Local
        client = boto3.client(
            'dynamodb',
            endpoint_url='http://localhost:8000',
            region_name='us-east-1'
        )
        table_name = 'sessions_mss_template-table'
        
        # Delete all existing items
        try:
            while True:
                response = client.scan(TableName=table_name, Limit=100)
                items = response.get('Items', [])
                
                if not items:
                    break
                
                for item in items:
                    client.delete_item(
                        TableName=table_name,
                        Key={'PK': item['PK']}
                    )
        except Exception as e:
            # Table might not exist yet, that's okay
            pass
        
        # Load mock data
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        for session in repo_mock.sessions:
            session_dto = SessionDynamoDTO.from_entity(session)
            dynamo_item = session_dto.to_dynamo()
            dynamo_item[repo.dynamo.partition_key] = repo.partition_key_format(session.session_id)
            repo.dynamo.dynamo_table.put_item(Item=dynamo_item)
        
        yield
        
        # Teardown: Clean up after test (optional)
        # We could clear the table here too, but it's not necessary
        # since setup will clear it before the next test
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_session_by_id(self):
        """Test retrieving a session by ID from DynamoDB"""
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        # Get first session from mock for comparison
        expected_session = repo_mock.sessions[0]
        
        # Get session from DynamoDB
        result = repo.get_session_by_id(expected_session.session_id)
        
        assert result.session_id == expected_session.session_id
        assert result.title == expected_session.title
        assert result.venue_name == expected_session.venue_name
        assert result.day == expected_session.day
        assert result.level_value == expected_session.level_value
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_session_by_id_not_found(self):
        """Test retrieving non-existent session raises NoItemsFound"""
        
        repo = SessionRepositoryDynamo()
        
        with pytest.raises(NoItemsFound):
            repo.get_session_by_id("invalid-session-id-999")
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_all_sessions(self):
        """Test retrieving all sessions from DynamoDB"""
        
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        result = repo.get_all_sessions()
        
        assert len(result) == len(repo_mock.sessions)
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_sessions_by_venue(self):
        """Test retrieving sessions filtered by venue using GSI-Venue"""
        
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        # Get a venue from mock data
        test_venue = repo_mock.sessions[0].venue_name
        
        # Get expected sessions from mock
        expected_sessions = [s for s in repo_mock.sessions if s.venue_name == test_venue]
        
        # Get sessions from DynamoDB
        result = repo.get_sessions_by_venue(test_venue)
        
        assert len(result) == len(expected_sessions)
        
        # Verify all sessions are from the correct venue
        for session in result:
            assert session.venue_name == test_venue
        
        # Verify ordering by start_datetime
        for i in range(len(result) - 1):
            assert result[i].start_datetime <= result[i + 1].start_datetime
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_sessions_by_day(self):
        """Test retrieving sessions filtered by day using GSI-Day"""
        
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        # Get a day from mock data
        test_day = repo_mock.sessions[0].day
        
        # Get expected sessions from mock
        expected_sessions = [s for s in repo_mock.sessions if s.day == test_day]
        
        # Get sessions from DynamoDB
        result = repo.get_sessions_by_day(test_day)
        
        assert len(result) == len(expected_sessions)
        
        # Verify all sessions are from the correct day
        for session in result:
            assert session.day == test_day
        
        # Verify ordering by start_datetime
        for i in range(len(result) - 1):
            assert result[i].start_datetime <= result[i + 1].start_datetime
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_sessions_by_level(self):
        """Test retrieving sessions filtered by level using GSI-Level"""
        
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        # Get a level from mock data
        test_level = repo_mock.sessions[0].level_value
        
        # Get expected sessions from mock
        expected_sessions = [s for s in repo_mock.sessions if s.level_value == test_level]
        
        # Get sessions from DynamoDB
        result = repo.get_sessions_by_level(test_level)
        
        assert len(result) == len(expected_sessions)
        
        # Verify all sessions are from the correct level
        for session in result:
            assert session.level_value == test_level
        
        # Verify ordering by start_datetime
        for i in range(len(result) - 1):
            assert result[i].start_datetime <= result[i + 1].start_datetime
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_sessions_by_venue_empty_result(self):
        """Test retrieving sessions with non-existent venue returns empty list"""
        
        repo = SessionRepositoryDynamo()
        
        result = repo.get_sessions_by_venue("NonExistentVenue")
        
        assert len(result) == 0
        assert result == []
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_sessions_by_day_empty_result(self):
        """Test retrieving sessions with non-existent day returns empty list"""
        
        repo = SessionRepositoryDynamo()
        
        result = repo.get_sessions_by_day("NonExistentDay")
        
        assert len(result) == 0
        assert result == []
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_sessions_by_level_empty_result(self):
        """Test retrieving sessions with non-existent level returns empty list"""
        
        repo = SessionRepositoryDynamo()
        
        result = repo.get_sessions_by_level(999)
        
        assert len(result) == 0
        assert result == []

    # @pytest.mark.skip(reason="Needs dynamoDB and working API")
    def test_sync_sessions_from_api(self):
        """Test syncing sessions from API to DynamoDB"""
        
        repo = SessionRepositoryDynamo()
        
        # Get initial count
        initial_sessions = repo.get_all_sessions()
        initial_count = len(initial_sessions)
        
        # Sync sessions from API
        result = repo.sync_sessions_from_api()
        
        # Verify return structure
        assert "inserted" in result
        assert "updated" in result
        assert isinstance(result["inserted"], int)
        assert isinstance(result["updated"], int)
        
        # Verify counts are non-negative
        assert result["inserted"] >= 0
        assert result["updated"] >= 0
        
        # Verify total count increased or stayed same
        final_sessions = repo.get_all_sessions()
        final_count = len(final_sessions)
        assert final_count >= initial_count
        
        # Verify the total matches inserted + updated
        assert final_count == initial_count + result["inserted"]
    
    @pytest.mark.skip(reason="Needs dynamoDB and working API")
    def test_sync_sessions_from_api_idempotent(self):
        """Test syncing sessions from API is idempotent (doesn't duplicate)"""
        
        repo = SessionRepositoryDynamo()
        
        # First sync
        result1 = repo.sync_sessions_from_api()
        count_after_first = len(repo.get_all_sessions())
        
        # Second sync - should update existing sessions, not insert duplicates
        result2 = repo.sync_sessions_from_api()
        count_after_second = len(repo.get_all_sessions())
        
        # On second sync, all sessions should be updates (not inserts)
        # Total count should remain the same
        assert count_after_second == count_after_first
        assert result2["inserted"] == 0
        assert result2["updated"] > 0
    
    @pytest.mark.skip(reason="Needs dynamoDB and working API")
    def test_sync_sessions_from_api_persists_to_dynamodb(self):
        """Test that synced sessions are properly persisted to DynamoDB"""
        
        repo = SessionRepositoryDynamo()
        
        # Sync sessions
        result = repo.sync_sessions_from_api()
        
        # Verify we can retrieve the synced sessions
        all_sessions = repo.get_all_sessions()
        
        # Verify all sessions have required attributes
        for session in all_sessions:
            assert session.session_id is not None
            assert session.title is not None
            assert session.venue_name is not None
            assert session.day is not None
            assert session.level_value is not None
            assert session.start_datetime is not None
    
    @pytest.mark.skip(reason="Needs dynamoDB and working API")
    def test_sync_sessions_from_api_gsi_indexes_work(self):
        """Test that GSI indexes work correctly after syncing sessions"""
        
        repo = SessionRepositoryDynamo()
        
        # Sync sessions from API
        repo.sync_sessions_from_api()
        
        # Get all sessions to find test data
        all_sessions = repo.get_all_sessions()
        
        if len(all_sessions) > 0:
            # Test GSI-Venue works
            test_venue = all_sessions[0].venue_name
            venue_sessions = repo.get_sessions_by_venue(test_venue)
            assert len(venue_sessions) > 0
            assert all(s.venue_name == test_venue for s in venue_sessions)
            
            # Test GSI-Day works
            test_day = all_sessions[0].day
            day_sessions = repo.get_sessions_by_day(test_day)
            assert len(day_sessions) > 0
            assert all(s.day == test_day for s in day_sessions)
            
            # Test GSI-Level works
            test_level = all_sessions[0].level_value
            level_sessions = repo.get_sessions_by_level(test_level)
            assert len(level_sessions) > 0
            assert all(s.level_value == test_level for s in level_sessions)
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_session_by_id_performance(self):
        """Test that get_session_by_id completes in less than 500ms"""
        import time
        
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        # Get first session from mock for testing
        test_session_id = repo_mock.sessions[0].session_id
        
        # Measure performance
        start_time = time.time()
        result = repo.get_session_by_id(test_session_id)
        end_time = time.time()
        
        elapsed_ms = (end_time - start_time) * 1000
        
        # Verify result is correct
        assert result.session_id == test_session_id
        
        # Verify performance is under 500ms
        assert elapsed_ms < 500, f"get_session_by_id took {elapsed_ms:.2f}ms, expected < 500ms"
    
    @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_all_sessions_paginated_with_page_size_only(self):
        """Test get_all_sessions_paginated with page_size only"""
        
        repo = SessionRepositoryDynamo()
        
        sessions, next_token = repo.get_all_sessions_paginated(page_size=2)
        
        assert len(sessions) <= 2
        # Should have next_token if there are more than 2 sessions
        if len(repo.get_all_sessions()) > 2:
            assert next_token is not None
    
    @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_all_sessions_paginated_with_page_size_and_token(self):
        """Test get_all_sessions_paginated with page_size and last_evaluated_key"""
        
        repo = SessionRepositoryDynamo()
        
        # Get first page
        page1, token1 = repo.get_all_sessions_paginated(page_size=2)
        
        # Get second page using token
        page2, token2 = repo.get_all_sessions_paginated(page_size=2, last_evaluated_key=token1)
        
        # Verify no overlap
        page1_ids = [s.session_id for s in page1]
        page2_ids = [s.session_id for s in page2]
        assert len(set(page1_ids) & set(page2_ids)) == 0
    
    @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_all_sessions_paginated_returns_correct_next_token(self):
        """Test pagination returns correct next_token when more results exist"""
        
        repo = SessionRepositoryDynamo()
        
        # Get first page with small page size
        sessions, next_token = repo.get_all_sessions_paginated(page_size=1)
        
        # Should have next_token if there are more than 1 session
        total_sessions = len(repo.get_all_sessions())
        if total_sessions > 1:
            assert next_token is not None
        else:
            assert next_token is None
    
    @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_all_sessions_paginated_returns_none_token_on_last_page(self):
        """Test pagination returns None next_token on last page"""
        
        repo = SessionRepositoryDynamo()
        
        # Get all sessions in one page
        sessions, next_token = repo.get_all_sessions_paginated(page_size=100)
        
        # Should not have next_token on last page
        assert next_token is None
    
    @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_all_sessions_paginated_expired_token_raises_error(self):
        """Test expired token raises ValueError"""
        
        repo = SessionRepositoryDynamo()
        
        # Create an expired token
        import time
        import base64
        import json
        
        expired_token_data = {
            'PK': 'SESSION#test',
            'issued_at': int(time.time()) - 400,  # 400 seconds ago (expired)
            'ttl': 300
        }
        
        expired_token = base64.b64encode(json.dumps(expired_token_data).encode('utf-8')).decode('utf-8')
        
        with pytest.raises(ValueError) as exc_info:
            repo.get_all_sessions_paginated(page_size=2, last_evaluated_key=expired_token)
        
        assert "expired" in str(exc_info.value).lower()
    
    @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_all_sessions_paginated_invalid_page_size_raises_error(self):
        """Test invalid page_size raises ValueError"""
        
        repo = SessionRepositoryDynamo()
        
        # Test page_size < 1
        with pytest.raises(ValueError) as exc_info:
            repo.get_all_sessions_paginated(page_size=0)
        assert "at least 1" in str(exc_info.value)
        
        # Test page_size > 100
        with pytest.raises(ValueError) as exc_info:
            repo.get_all_sessions_paginated(page_size=101)
        assert "cannot exceed 100" in str(exc_info.value)
