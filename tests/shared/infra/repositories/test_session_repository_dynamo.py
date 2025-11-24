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
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_all_sessions_paginated_with_page_size_only(self):
        """Test get_all_sessions_paginated with page_size only"""
        
        repo = SessionRepositoryDynamo()
        
        sessions, next_token = repo.get_all_sessions_paginated(page_size=2)
        
        assert len(sessions) <= 2
        # Should have next_token if there are more than 2 sessions
        if len(repo.get_all_sessions()) > 2:
            assert next_token is not None
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
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
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
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
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_all_sessions_paginated_returns_none_token_on_last_page(self):
        """Test pagination returns None next_token on last page"""
        
        repo = SessionRepositoryDynamo()
        
        # Get all sessions in one page
        sessions, next_token = repo.get_all_sessions_paginated(page_size=100)
        
        # Should not have next_token on last page
        assert next_token is None
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
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
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
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

    # ========== Property-Based Tests for search_sessions ==========
    
    def test_property_page_size_limit(self):
        """
        Property test: Page size limit
        Feature: intelligent-session-search, Property 7: Page size limit
        Validates: Requirements 3.2
        
        For any valid page_size value, the number of returned sessions should not exceed that value.
        """
        from hypothesis import given, strategies as st, settings
        
        repo = SessionRepositoryDynamo()
        
        @given(page_size=st.integers(min_value=1, max_value=100))
        @settings(max_examples=100)
        def property_test(page_size):
            sessions, _ = repo.search_sessions(page_size=page_size)
            assert len(sessions) <= page_size, f"Returned {len(sessions)} sessions, expected <= {page_size}"
        
        property_test()
    
    def test_property_next_page_token_presence(self):
        """
        Property test: Next page token presence
        Feature: intelligent-session-search, Property 8: Next page token presence
        Validates: Requirements 3.3
        
        For any search where total results exceed page_size, the response should include a non-null next_page_token.
        """
        from hypothesis import given, strategies as st, settings, assume
        
        repo = SessionRepositoryDynamo()
        
        @given(page_size=st.integers(min_value=1, max_value=3))
        @settings(max_examples=100)
        def property_test(page_size):
            # Get total count first
            all_sessions, _ = repo.search_sessions(page_size=100)
            total_count = len(all_sessions)
            
            # Only test when we have more sessions than page_size
            assume(total_count > page_size)
            
            sessions, next_token = repo.search_sessions(page_size=page_size)
            
            # If there are more results, next_token should be present
            if len(sessions) == page_size and total_count > page_size:
                assert next_token is not None, f"Expected next_page_token when {total_count} total > {page_size} page_size"
        
        property_test()
    
    def test_property_pagination_continuation(self):
        """
        Property test: Pagination continuation
        Feature: intelligent-session-search, Property 9: Pagination continuation
        Validates: Requirements 3.4
        
        For any valid next_page_token, using it should return the next set of results without duplicates from the previous page.
        """
        from hypothesis import given, strategies as st, settings, assume
        
        repo = SessionRepositoryDynamo()
        
        @given(page_size=st.integers(min_value=1, max_value=3))
        @settings(max_examples=100)
        def property_test(page_size):
            # Get first page
            page1, token1 = repo.search_sessions(page_size=page_size)
            
            # Only test if there's a next page
            assume(token1 is not None)
            
            # Get second page
            page2, token2 = repo.search_sessions(page_size=page_size, last_evaluated_key=token1)
            
            # Verify no duplicates
            page1_ids = set(s.session_id for s in page1)
            page2_ids = set(s.session_id for s in page2)
            
            overlap = page1_ids & page2_ids
            assert len(overlap) == 0, f"Found {len(overlap)} duplicate sessions between pages"
        
        property_test()
    
    def test_property_final_page_token_absence(self):
        """
        Property test: Final page token absence
        Feature: intelligent-session-search, Property 10: Final page token absence
        Validates: Requirements 3.5
        
        For any search where the current page contains the last results, the next_page_token should be null.
        """
        from hypothesis import given, strategies as st, settings
        
        repo = SessionRepositoryDynamo()
        
        @given(page_size=st.integers(min_value=50, max_value=100))
        @settings(max_examples=100)
        def property_test(page_size):
            # Get all sessions with large page size
            sessions, next_token = repo.search_sessions(page_size=page_size)
            
            # If we got fewer sessions than page_size, this is the last page
            if len(sessions) < page_size:
                assert next_token is None, f"Expected no next_token on last page (got {len(sessions)} < {page_size})"
        
        property_test()
    
    def test_property_keyword_relevance_ordering(self):
        """
        Property test: Keyword relevance ordering
        Feature: intelligent-session-search, Property 11: Keyword relevance ordering
        Validates: Requirements 5.1
        
        For any keyword search, sessions with keyword matches in title should appear before sessions 
        with matches only in abstract, which should appear before sessions with matches only in topics/areas.
        """
        from hypothesis import given, strategies as st, settings
        
        repo = SessionRepositoryDynamo()
        
        @given(keyword=st.sampled_from(["aws", "security", "serverless", "data"]))
        @settings(max_examples=100)
        def property_test(keyword):
            sessions, _ = repo.search_sessions(keywords=keyword)
            
            # Calculate scores for each session
            scores = []
            for session in sessions:
                score = repo._calculate_relevance_score(session, [keyword.lower()])
                scores.append(score)
            
            # Verify scores are in descending order (higher relevance first)
            for i in range(len(scores) - 1):
                assert scores[i] >= scores[i + 1], \
                    f"Relevance ordering violated: scores[{i}]={scores[i]} < scores[{i+1}]={scores[i+1]}"
        
        property_test()
    
    def test_property_default_datetime_ordering(self):
        """
        Property test: Default datetime ordering
        Feature: intelligent-session-search, Property 12: Default datetime ordering
        Validates: Requirements 5.2
        
        For any search without keywords, results should be ordered by start_datetime in ascending order (earlier sessions first).
        """
        from hypothesis import given, strategies as st, settings
        
        repo = SessionRepositoryDynamo()
        
        @given(
            day=st.sampled_from([None, "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
            venue=st.sampled_from([None, "Venetian", "Mandalay Bay", "MGM Grand"]),
            level=st.sampled_from([None, 100, 200, 300, 400])
        )
        @settings(max_examples=100)
        def property_test(day, venue, level):
            # Search without keywords
            sessions, _ = repo.search_sessions(day=day, venue=venue, level=level)
            
            # Verify chronological ordering
            for i in range(len(sessions) - 1):
                assert sessions[i].start_datetime <= sessions[i + 1].start_datetime, \
                    f"Datetime ordering violated: sessions[{i}].start_datetime > sessions[{i+1}].start_datetime"
        
        property_test()
    
    def test_property_relevance_tie_breaking(self):
        """
        Property test: Relevance tie-breaking
        Feature: intelligent-session-search, Property 13: Relevance tie-breaking
        Validates: Requirements 5.3
        
        For any two sessions with equal relevance scores in a keyword search, 
        the session with earlier start_datetime should appear first.
        """
        from hypothesis import given, strategies as st, settings
        
        repo = SessionRepositoryDynamo()
        
        @given(keyword=st.sampled_from(["aws", "security", "serverless"]))
        @settings(max_examples=100)
        def property_test(keyword):
            sessions, _ = repo.search_sessions(keywords=keyword)
            
            # Calculate scores and group by score
            sessions_with_scores = []
            for session in sessions:
                score = repo._calculate_relevance_score(session, [keyword.lower()])
                sessions_with_scores.append((session, score))
            
            # Check tie-breaking within each score group
            current_score = None
            previous_datetime = None
            
            for session, score in sessions_with_scores:
                if current_score is None:
                    current_score = score
                    previous_datetime = session.start_datetime
                elif score == current_score:
                    # Same score - verify datetime ordering
                    assert previous_datetime <= session.start_datetime, \
                        f"Tie-breaking violated: sessions with same score not ordered by datetime"
                    previous_datetime = session.start_datetime
                else:
                    # New score group
                    current_score = score
                    previous_datetime = session.start_datetime
        
        property_test()
    
    # ========== Integration Tests for search_sessions ==========
    
    def test_search_sessions_gsi_query_execution(self):
        """Test that search uses GSI queries when indexed filters are provided"""
        
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        # Test Level GSI (highest priority)
        sessions, _ = repo.search_sessions(level=200)
        assert len(sessions) > 0
        assert all(s.level_value == 200 for s in sessions)
        
        # Test Venue GSI
        test_venue = repo_mock.sessions[0].venue_name
        sessions, _ = repo.search_sessions(venue=test_venue)
        assert len(sessions) > 0
        assert all(s.venue_name == test_venue for s in sessions)
        
        # Test Day GSI
        test_day = repo_mock.sessions[0].day
        sessions, _ = repo.search_sessions(day=test_day)
        assert len(sessions) > 0
        assert all(s.day == test_day for s in sessions)
    
    def test_search_sessions_keyword_filtering_performance(self):
        """Test keyword filtering completes in reasonable time"""
        import time
        
        repo = SessionRepositoryDynamo()
        
        start_time = time.time()
        sessions, _ = repo.search_sessions(keywords="aws serverless")
        end_time = time.time()
        
        elapsed_ms = (end_time - start_time) * 1000
        
        # Verify results are correct
        assert len(sessions) >= 0
        
        # Verify performance is under 500ms
        assert elapsed_ms < 500, f"Keyword search took {elapsed_ms:.2f}ms, expected < 500ms"
    
    def test_search_sessions_pagination_with_large_dataset(self):
        """Test pagination works correctly with large result sets"""
        
        repo = SessionRepositoryDynamo()
        
        # Get all sessions in small pages
        all_sessions_paginated = []
        next_token = None
        page_count = 0
        max_pages = 10  # Safety limit
        
        while page_count < max_pages:
            sessions, next_token = repo.search_sessions(page_size=1, last_evaluated_key=next_token)
            all_sessions_paginated.extend(sessions)
            page_count += 1
            
            if next_token is None:
                break
        
        # Get all sessions in one query
        all_sessions_direct, _ = repo.search_sessions(page_size=100)
        
        # Verify we got the same sessions (order may differ)
        paginated_ids = set(s.session_id for s in all_sessions_paginated)
        direct_ids = set(s.session_id for s in all_sessions_direct)
        
        assert paginated_ids == direct_ids, "Pagination returned different sessions than direct query"
    
    # ========== Property-Based Tests for Enhanced Session Search ==========
    
    def test_property_venue_filtering_correctness(self):
        """
        Property test: Venue filtering correctness
        Feature: enhanced-session-search, Property 1: Venue filtering correctness
        Validates: Requirements 1.1
        
        For any venue name and set of sessions, filtering by that venue should return 
        only sessions where venue_name equals that venue.
        """
        from hypothesis import given, strategies as st, settings, assume
        
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        # Get all unique venues from mock data
        unique_venues = list(set(s.venue_name for s in repo_mock.sessions))
        
        @given(venue=st.sampled_from(unique_venues))
        @settings(max_examples=100)
        def property_test(venue):
            # Get sessions filtered by venue
            sessions = repo.get_sessions_by_venue(venue)
            
            # Verify all returned sessions have the correct venue
            for session in sessions:
                assert session.venue_name == venue, \
                    f"Session {session.session_id} has venue '{session.venue_name}', expected '{venue}'"
        
        property_test()
    
    def test_property_day_filtering_correctness(self):
        """
        Property test: Day filtering correctness
        Feature: enhanced-session-search, Property 2: Day filtering correctness
        Validates: Requirements 1.2
        
        For any day name and set of sessions, filtering by that day should return 
        only sessions where day equals that day.
        """
        from hypothesis import given, strategies as st, settings, assume
        
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        # Get all unique days from mock data
        unique_days = list(set(s.day for s in repo_mock.sessions))
        
        @given(day=st.sampled_from(unique_days))
        @settings(max_examples=100)
        def property_test(day):
            # Get sessions filtered by day
            sessions = repo.get_sessions_by_day(day)
            
            # Verify all returned sessions have the correct day
            for session in sessions:
                assert session.day == day, \
                    f"Session {session.session_id} has day '{session.day}', expected '{day}'"
        
        property_test()
    
    def test_property_level_filtering_correctness(self):
        """
        Property test: Level filtering correctness
        Feature: enhanced-session-search, Property 3: Level filtering correctness
        Validates: Requirements 1.3
        
        For any level value and set of sessions, filtering by that level should return 
        only sessions where level_value equals that level.
        """
        from hypothesis import given, strategies as st, settings, assume
        
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        # Get all unique levels from mock data
        unique_levels = list(set(s.level_value for s in repo_mock.sessions))
        
        @given(level=st.sampled_from(unique_levels))
        @settings(max_examples=100)
        def property_test(level):
            # Get sessions filtered by level
            sessions = repo.get_sessions_by_level(level)
            
            # Verify all returned sessions have the correct level
            for session in sessions:
                assert session.level_value == level, \
                    f"Session {session.session_id} has level {session.level_value}, expected {level}"
        
        property_test()
    
    def test_property_combined_filter_correctness(self):
        """
        Property test: Combined filter correctness
        Feature: enhanced-session-search, Property 4: Combined filter correctness
        Validates: Requirements 1.4, 1.5
        
        For any combination of venue, day, and level filters, all returned sessions 
        should match all provided filter criteria.
        """
        from hypothesis import given, strategies as st, settings, assume
        from itertools import product
        
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        # Get all unique values from mock data
        unique_venues = list(set(s.venue_name for s in repo_mock.sessions))
        unique_days = list(set(s.day for s in repo_mock.sessions))
        unique_levels = list(set(s.level_value for s in repo_mock.sessions))
        
        @given(
            venue=st.sampled_from(unique_venues),
            day=st.sampled_from(unique_days),
            level=st.sampled_from(unique_levels)
        )
        @settings(max_examples=100)
        def property_test(venue, day, level):
            # Test venue + day combination
            sessions, _ = repo.search_sessions(venue=venue, day=day)
            for session in sessions:
                assert session.venue_name == venue, \
                    f"Session {session.session_id} has venue '{session.venue_name}', expected '{venue}'"
                assert session.day == day, \
                    f"Session {session.session_id} has day '{session.day}', expected '{day}'"
            
            # Test venue + level combination
            sessions, _ = repo.search_sessions(venue=venue, level=level)
            for session in sessions:
                assert session.venue_name == venue, \
                    f"Session {session.session_id} has venue '{session.venue_name}', expected '{venue}'"
                assert session.level_value == level, \
                    f"Session {session.session_id} has level {session.level_value}, expected {level}"
            
            # Test day + level combination
            sessions, _ = repo.search_sessions(day=day, level=level)
            for session in sessions:
                assert session.day == day, \
                    f"Session {session.session_id} has day '{session.day}', expected '{day}'"
                assert session.level_value == level, \
                    f"Session {session.session_id} has level {session.level_value}, expected {level}"
            
            # Test all three filters combined
            sessions, _ = repo.search_sessions(venue=venue, day=day, level=level)
            for session in sessions:
                assert session.venue_name == venue, \
                    f"Session {session.session_id} has venue '{session.venue_name}', expected '{venue}'"
                assert session.day == day, \
                    f"Session {session.session_id} has day '{session.day}', expected '{day}'"
                assert session.level_value == level, \
                    f"Session {session.session_id} has level {session.level_value}, expected {level}"
        
        property_test()
    
    def test_property_gsi_ordering_preservation(self):
        """
        Property test: GSI ordering preservation
        Feature: enhanced-session-search, Property 5: GSI ordering preservation
        Validates: Requirements 1.6
        
        For any GSI query (venue, day, or level), the returned sessions should be 
        ordered by start_datetime in ascending order.
        """
        from hypothesis import given, strategies as st, settings, assume
        
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        # Get all unique values from mock data
        unique_venues = list(set(s.venue_name for s in repo_mock.sessions))
        unique_days = list(set(s.day for s in repo_mock.sessions))
        unique_levels = list(set(s.level_value for s in repo_mock.sessions))
        
        @given(
            filter_type=st.sampled_from(['venue', 'day', 'level']),
            venue=st.sampled_from(unique_venues),
            day=st.sampled_from(unique_days),
            level=st.sampled_from(unique_levels)
        )
        @settings(max_examples=100)
        def property_test(filter_type, venue, day, level):
            # Get sessions based on filter type
            if filter_type == 'venue':
                sessions = repo.get_sessions_by_venue(venue)
            elif filter_type == 'day':
                sessions = repo.get_sessions_by_day(day)
            else:  # level
                sessions = repo.get_sessions_by_level(level)
            
            # Skip if no sessions returned
            assume(len(sessions) > 1)
            
            # Verify ordering by start_datetime
            for i in range(len(sessions) - 1):
                assert sessions[i].start_datetime <= sessions[i + 1].start_datetime, \
                    f"Ordering violated: sessions[{i}].start_datetime ({sessions[i].start_datetime}) > " \
                    f"sessions[{i+1}].start_datetime ({sessions[i+1].start_datetime})"
        
        property_test()

    # @pytest.mark.skip(reason="Needs dynamoDB")
    def test_search_sessions_with_speaker_filter(self):
        """
        Integration test: Speaker filtering with DynamoDB
        Test speaker filter returns only matching sessions
        Validates: Requirements 2.1, 2.2, 5.4
        """
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        # Find a speaker name from mock data
        test_speaker = None
        for session in repo_mock.sessions:
            if session.speakers and len(session.speakers) > 0:
                test_speaker = session.speakers[0].get('displayName', '')
                if test_speaker:
                    break
        
        # Skip test if no speakers found in mock data
        if not test_speaker:
            pytest.skip("No speakers found in mock data")
        
        # Search with speaker filter
        sessions, _ = repo.search_sessions(speaker=test_speaker)
        
        # Verify all sessions have a matching speaker
        for session in sessions:
            found_match = False
            for speaker in session.speakers:
                display_name = speaker.get('displayName', '').lower()
                company = speaker.get('company', '').lower()
                search_term = test_speaker.lower()
                
                if search_term in display_name or search_term in company:
                    found_match = True
                    break
            
            assert found_match, \
                f"Session {session.session_id} does not have a speaker matching '{test_speaker}'"
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
    def test_search_sessions_speaker_with_gsi_query(self):
        """
        Integration test: Speaker filter with GSI queries
        Test speaker filter works correctly when combined with indexed filters
        Validates: Requirements 2.1, 2.2, 5.4
        """
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        # Find a speaker and venue from mock data
        test_speaker = None
        test_venue = None
        
        for session in repo_mock.sessions:
            if session.speakers and len(session.speakers) > 0:
                test_speaker = session.speakers[0].get('displayName', '')
                test_venue = session.venue_name
                if test_speaker and test_venue:
                    break
        
        # Skip test if no speakers found in mock data
        if not test_speaker or not test_venue:
            pytest.skip("No speakers or venue found in mock data")
        
        # Search with speaker + venue filter (should use GSI-Venue + speaker FilterExpression)
        sessions, _ = repo.search_sessions(speaker=test_speaker, venue=test_venue)
        
        # Verify all sessions match both filters
        for session in sessions:
            # Check venue
            assert session.venue_name == test_venue, \
                f"Session {session.session_id} has venue '{session.venue_name}', expected '{test_venue}'"
            
            # Check speaker
            found_match = False
            for speaker in session.speakers:
                display_name = speaker.get('displayName', '').lower()
                company = speaker.get('company', '').lower()
                search_term = test_speaker.lower()
                
                if search_term in display_name or search_term in company:
                    found_match = True
                    break
            
            assert found_match, \
                f"Session {session.session_id} does not have a speaker matching '{test_speaker}'"
    
    # @pytest.mark.skip(reason="Needs dynamoDB")
    def test_search_sessions_speaker_case_insensitive(self):
        """
        Integration test: Speaker case-insensitive matching
        Test speaker search works with different casings
        Validates: Requirements 2.2, 5.4
        """
        repo = SessionRepositoryDynamo()
        repo_mock = SessionRepositoryMock()
        
        # Find a speaker name from mock data
        test_speaker = None
        for session in repo_mock.sessions:
            if session.speakers and len(session.speakers) > 0:
                test_speaker = session.speakers[0].get('displayName', '')
                if test_speaker and len(test_speaker) > 3:
                    break
        
        # Skip test if no speakers found in mock data
        if not test_speaker:
            pytest.skip("No speakers found in mock data")
        
        # Search with different casings
        sessions_lower, _ = repo.search_sessions(speaker=test_speaker.lower())
        sessions_upper, _ = repo.search_sessions(speaker=test_speaker.upper())
        sessions_title, _ = repo.search_sessions(speaker=test_speaker.title())
        
        # All should return the same sessions (order may differ)
        lower_ids = set(s.session_id for s in sessions_lower)
        upper_ids = set(s.session_id for s in sessions_upper)
        title_ids = set(s.session_id for s in sessions_title)
        
        assert lower_ids == upper_ids == title_ids, \
            "Case-insensitive matching failed: different casings returned different results"
