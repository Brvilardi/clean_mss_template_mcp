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
    
    def test_get_all_sessions_paginated_returns_correct_page_size(self):
        """Test get_all_sessions_paginated returns correct page size"""
        repo = SessionRepositoryMock()
        sessions, next_token = repo.get_all_sessions_paginated(page_size=2)
        
        assert len(sessions) == 2
        assert next_token is not None
    
    def test_get_all_sessions_paginated_with_multiple_pages(self):
        """Test get_all_sessions_paginated with multiple pages"""
        repo = SessionRepositoryMock()
        
        # First page
        page1, token1 = repo.get_all_sessions_paginated(page_size=2)
        assert len(page1) == 2
        assert token1 is not None
        
        # Second page
        page2, token2 = repo.get_all_sessions_paginated(page_size=2, last_evaluated_key=token1)
        assert len(page2) == 2
        assert token2 is not None
        
        # Third page (last page with 1 item)
        page3, token3 = repo.get_all_sessions_paginated(page_size=2, last_evaluated_key=token2)
        assert len(page3) == 1
        assert token3 is None
    
    def test_get_all_sessions_paginated_token_works_across_requests(self):
        """Test pagination token works across requests"""
        repo = SessionRepositoryMock()
        
        # Get first page
        page1, token1 = repo.get_all_sessions_paginated(page_size=3)
        
        # Get second page using token
        page2, token2 = repo.get_all_sessions_paginated(page_size=3, last_evaluated_key=token1)
        
        # Verify no overlap
        page1_ids = [s.session_id for s in page1]
        page2_ids = [s.session_id for s in page2]
        assert len(set(page1_ids) & set(page2_ids)) == 0
    
    def test_get_all_sessions_paginated_last_page_returns_none_token(self):
        """Test last page returns None next_token"""
        repo = SessionRepositoryMock()
        
        # Get all sessions in one page
        sessions, next_token = repo.get_all_sessions_paginated(page_size=100)
        
        assert len(sessions) == 5
        assert next_token is None
    
    def test_get_all_sessions_paginated_expired_token_raises_error(self):
        """Test expired token raises ValueError"""
        repo = SessionRepositoryMock()
        
        # Create an expired token (issued_at in the past)
        import time
        from src.shared.helpers.pagination.pagination_helper import PaginationHelper
        
        pagination_helper = PaginationHelper()
        expired_token_data = {
            'index': 2,
            'issued_at': int(time.time()) - 400,  # 400 seconds ago (expired)
            'ttl': 300
        }
        
        import base64
        import json
        expired_token = base64.b64encode(json.dumps(expired_token_data).encode('utf-8')).decode('utf-8')
        
        with pytest.raises(ValueError) as exc_info:
            repo.get_all_sessions_paginated(page_size=2, last_evaluated_key=expired_token)
        
        assert "expired" in str(exc_info.value).lower()
    
    def test_get_all_sessions_paginated_invalid_page_size_raises_error(self):
        """Test invalid page_size raises ValueError"""
        repo = SessionRepositoryMock()
        
        # Test page_size < 1
        with pytest.raises(ValueError) as exc_info:
            repo.get_all_sessions_paginated(page_size=0)
        assert "at least 1" in str(exc_info.value)
        
        # Test page_size > 100
        with pytest.raises(ValueError) as exc_info:
            repo.get_all_sessions_paginated(page_size=101)
        assert "cannot exceed 100" in str(exc_info.value)
        
        # Test page_size not an integer
        with pytest.raises(ValueError) as exc_info:
            repo.get_all_sessions_paginated(page_size="invalid")
        assert "must be an integer" in str(exc_info.value)

    # ========== Property-Based Tests for search_sessions ==========
    
    def test_search_sessions_property_combined_filter_matching(self):
        """
        Property test: Combined filter matching
        Feature: intelligent-session-search, Property 1: Combined filter matching
        Validates: Requirements 1.1
        
        For any combination of day, venue, level, and keywords filters,
        all returned sessions should match all provided filter criteria.
        """
        from hypothesis import given, strategies as st, settings
        
        repo = SessionRepositoryMock()
        
        # Define valid values based on mock data
        valid_days = ["Thursday", "Friday", "Saturday", "Sunday"]
        valid_venues = ["Mandalay Bay", "Venetian", "MGM Grand", "Wynn", "Caesars Forum"]
        valid_levels = [100, 200, 300, 400]
        valid_keywords = ["AWS", "security", "serverless", "data", "container"]
        
        @given(
            day=st.one_of(st.none(), st.sampled_from(valid_days)),
            venue=st.one_of(st.none(), st.sampled_from(valid_venues)),
            level=st.one_of(st.none(), st.sampled_from(valid_levels)),
            keywords=st.one_of(st.none(), st.sampled_from(valid_keywords))
        )
        @settings(max_examples=100)
        def property_test(day, venue, level, keywords):
            sessions, _ = repo.search_sessions(
                day=day,
                venue=venue,
                level=level,
                keywords=keywords
            )
            
            # Verify all returned sessions match all provided filters
            for session in sessions:
                if day is not None:
                    assert session.day == day, f"Session day {session.day} doesn't match filter {day}"
                
                if venue is not None:
                    assert session.venue_name == venue, f"Session venue {session.venue_name} doesn't match filter {venue}"
                
                if level is not None:
                    assert session.level_value == level, f"Session level {session.level_value} doesn't match filter {level}"
                
                if keywords is not None and keywords.strip():
                    # Verify keyword appears in at least one searchable field
                    keyword_lower = keywords.lower()
                    found = (
                        keyword_lower in session.title.lower() or
                        keyword_lower in session.abstract.lower() or
                        any(keyword_lower in topic.lower() for topic in session.topics) or
                        any(keyword_lower in area.lower() for area in session.areas_of_interest)
                    )
                    assert found, f"Keyword '{keywords}' not found in session {session.session_id}"
        
        property_test()
    
    def test_search_sessions_property_partial_filter_matching(self):
        """
        Property test: Partial filter matching
        Feature: intelligent-session-search, Property 2: Partial filter matching
        Validates: Requirements 1.2
        
        For any subset of available filters, all returned sessions should match
        only the provided filters and ignore unprovided filters.
        """
        from hypothesis import given, strategies as st, settings
        
        repo = SessionRepositoryMock()
        
        @given(
            use_day=st.booleans(),
            use_venue=st.booleans(),
            use_level=st.booleans()
        )
        @settings(max_examples=100)
        def property_test(use_day, use_venue, use_level):
            # Build filter parameters
            day = "Friday" if use_day else None
            venue = "Venetian" if use_venue else None
            level = 200 if use_level else None
            
            sessions, _ = repo.search_sessions(
                day=day,
                venue=venue,
                level=level
            )
            
            # Verify only provided filters are applied
            for session in sessions:
                if use_day:
                    assert session.day == "Friday"
                if use_venue:
                    assert session.venue_name == "Venetian"
                if use_level:
                    assert session.level_value == 200
        
        property_test()
    
    def test_search_sessions_property_keyword_field_coverage(self):
        """
        Property test: Keyword field coverage
        Feature: intelligent-session-search, Property 4: Keyword field coverage
        Validates: Requirements 2.1
        
        For any keyword, if it appears in a session's title, abstract, topics,
        or areas_of_interest, that session should be included in search results.
        """
        from hypothesis import given, strategies as st, settings
        
        repo = SessionRepositoryMock()
        
        # Get all unique words from all sessions
        all_words = set()
        for session in repo.sessions:
            all_words.update(session.title.lower().split())
            all_words.update(session.abstract.lower().split())
            for topic in session.topics:
                all_words.update(topic.lower().split())
            for area in session.areas_of_interest:
                all_words.update(area.lower().split())
        
        # Filter to reasonable words (length > 3)
        searchable_words = [w for w in all_words if len(w) > 3]
        
        @given(keyword=st.sampled_from(searchable_words))
        @settings(max_examples=100)
        def property_test(keyword):
            sessions, _ = repo.search_sessions(keywords=keyword)
            
            # Find all sessions that should match this keyword
            expected_matches = []
            for session in repo.sessions:
                if (keyword in session.title.lower() or
                    keyword in session.abstract.lower() or
                    any(keyword in topic.lower() for topic in session.topics) or
                    any(keyword in area.lower() for area in session.areas_of_interest)):
                    expected_matches.append(session.session_id)
            
            # Verify all expected matches are in results
            result_ids = [s.session_id for s in sessions]
            for expected_id in expected_matches:
                assert expected_id in result_ids, f"Session {expected_id} with keyword '{keyword}' not in results"
        
        property_test()
    
    def test_search_sessions_property_case_insensitive_keyword_matching(self):
        """
        Property test: Case-insensitive keyword matching
        Feature: intelligent-session-search, Property 5: Case-insensitive keyword matching
        Validates: Requirements 2.6
        
        For any keyword with different casing, the search should return the same results.
        """
        from hypothesis import given, strategies as st, settings
        
        repo = SessionRepositoryMock()
        
        keywords = ["security", "serverless", "lambda", "data", "aws"]
        
        @given(keyword=st.sampled_from(keywords))
        @settings(max_examples=100)
        def property_test(keyword):
            # Search with lowercase
            sessions_lower, _ = repo.search_sessions(keywords=keyword.lower())
            
            # Search with uppercase
            sessions_upper, _ = repo.search_sessions(keywords=keyword.upper())
            
            # Search with mixed case
            sessions_mixed, _ = repo.search_sessions(keywords=keyword.capitalize())
            
            # All should return same session IDs
            ids_lower = [s.session_id for s in sessions_lower]
            ids_upper = [s.session_id for s in sessions_upper]
            ids_mixed = [s.session_id for s in sessions_mixed]
            
            assert ids_lower == ids_upper, f"Case sensitivity issue: {keyword.lower()} != {keyword.upper()}"
            assert ids_lower == ids_mixed, f"Case sensitivity issue: {keyword.lower()} != {keyword.capitalize()}"
        
        property_test()
    
    def test_search_sessions_property_multiple_keyword_or_logic(self):
        """
        Property test: Multiple keyword OR logic
        Feature: intelligent-session-search, Property 6: Multiple keyword OR logic
        Validates: Requirements 2.7
        
        For any multi-word keyword string, sessions matching any of the individual
        keywords should be included in results (OR logic, not AND).
        """
        from hypothesis import given, strategies as st, settings
        
        repo = SessionRepositoryMock()
        
        @given(
            keyword1=st.sampled_from(["security", "serverless", "data"]),
            keyword2=st.sampled_from(["aws", "lambda", "analytics"])
        )
        @settings(max_examples=100)
        def property_test(keyword1, keyword2):
            # Search with combined keywords
            combined_keywords = f"{keyword1} {keyword2}"
            sessions_combined, _ = repo.search_sessions(keywords=combined_keywords)
            
            # Search with individual keywords
            sessions_kw1, _ = repo.search_sessions(keywords=keyword1)
            sessions_kw2, _ = repo.search_sessions(keywords=keyword2)
            
            # Combined should include all sessions from either keyword (OR logic)
            ids_combined = set(s.session_id for s in sessions_combined)
            ids_kw1 = set(s.session_id for s in sessions_kw1)
            ids_kw2 = set(s.session_id for s in sessions_kw2)
            
            # Union of individual searches should equal combined search
            expected_ids = ids_kw1 | ids_kw2
            assert ids_combined == expected_ids, f"OR logic failed: combined={ids_combined}, expected={expected_ids}"
        
        property_test()
    
    # ========== Unit Tests for search_sessions ==========
    
    def test_search_sessions_empty_filters_returns_all(self):
        """Test search with no filters returns all sessions"""
        repo = SessionRepositoryMock()
        sessions, next_token = repo.search_sessions()
        
        assert len(sessions) == 5
        assert next_token is None
    
    def test_search_sessions_day_only(self):
        """Test search with day filter only"""
        repo = SessionRepositoryMock()
        sessions, _ = repo.search_sessions(day="Friday")
        
        assert len(sessions) == 2
        assert all(s.day == "Friday" for s in sessions)
    
    def test_search_sessions_venue_only(self):
        """Test search with venue filter only"""
        repo = SessionRepositoryMock()
        sessions, _ = repo.search_sessions(venue="Venetian")
        
        assert len(sessions) == 1
        assert sessions[0].venue_name == "Venetian"
    
    def test_search_sessions_level_only(self):
        """Test search with level filter only"""
        repo = SessionRepositoryMock()
        sessions, _ = repo.search_sessions(level=200)
        
        assert len(sessions) == 2
        assert all(s.level_value == 200 for s in sessions)
    
    def test_search_sessions_keywords_only(self):
        """Test search with keywords filter only"""
        repo = SessionRepositoryMock()
        sessions, _ = repo.search_sessions(keywords="serverless")
        
        assert len(sessions) >= 1
        # Verify keyword appears in at least one field
        for session in sessions:
            found = (
                "serverless" in session.title.lower() or
                "serverless" in session.abstract.lower() or
                any("serverless" in topic.lower() for topic in session.topics) or
                any("serverless" in area.lower() for area in session.areas_of_interest)
            )
            assert found
    
    def test_search_sessions_combined_filters(self):
        """Test search with multiple filters combined"""
        repo = SessionRepositoryMock()
        sessions, _ = repo.search_sessions(day="Friday", level=200)
        
        assert len(sessions) == 2
        assert all(s.day == "Friday" and s.level_value == 200 for s in sessions)
    
    def test_search_sessions_empty_result(self):
        """Test search that returns no results"""
        repo = SessionRepositoryMock()
        sessions, _ = repo.search_sessions(day="Monday")
        
        assert len(sessions) == 0
        assert sessions == []
    
    def test_search_sessions_pagination_page_size(self):
        """Test search respects page_size parameter"""
        repo = SessionRepositoryMock()
        sessions, next_token = repo.search_sessions(page_size=2)
        
        assert len(sessions) == 2
        assert next_token is not None
    
    def test_search_sessions_pagination_continuation(self):
        """Test pagination continuation with next_token"""
        repo = SessionRepositoryMock()
        
        # First page
        page1, token1 = repo.search_sessions(page_size=2)
        assert len(page1) == 2
        assert token1 is not None
        
        # Second page
        page2, token2 = repo.search_sessions(page_size=2, last_evaluated_key=token1)
        assert len(page2) == 2
        
        # Verify no overlap
        page1_ids = [s.session_id for s in page1]
        page2_ids = [s.session_id for s in page2]
        assert len(set(page1_ids) & set(page2_ids)) == 0
    
    def test_search_sessions_relevance_ordering(self):
        """Test keyword search orders by relevance"""
        repo = SessionRepositoryMock()
        sessions, _ = repo.search_sessions(keywords="aws")
        
        # Verify results are ordered by relevance (title matches should be first)
        # All sessions should have keyword in some field
        assert len(sessions) > 0
        
        # Calculate scores manually to verify ordering
        scores = []
        for session in sessions:
            score = repo._calculate_relevance_score(session, ["aws"])
            scores.append(score)
        
        # Verify scores are in descending order
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1], "Results not ordered by relevance"
    
    def test_search_sessions_datetime_ordering_without_keywords(self):
        """Test search without keywords orders by start_datetime"""
        repo = SessionRepositoryMock()
        sessions, _ = repo.search_sessions(day="Friday")
        
        # Verify chronological ordering
        for i in range(len(sessions) - 1):
            assert sessions[i].start_datetime <= sessions[i + 1].start_datetime
    
    def test_search_sessions_invalid_page_size(self):
        """Test search with invalid page_size raises ValueError"""
        repo = SessionRepositoryMock()
        
        with pytest.raises(ValueError):
            repo.search_sessions(page_size=0)
        
        with pytest.raises(ValueError):
            repo.search_sessions(page_size=101)
    
    def test_search_sessions_multiple_keywords(self):
        """Test search with multiple space-separated keywords"""
        repo = SessionRepositoryMock()
        sessions, _ = repo.search_sessions(keywords="serverless lambda")
        
        # Should return sessions matching either keyword
        assert len(sessions) >= 1
        
        for session in sessions:
            # At least one keyword should match
            found = (
                "serverless" in session.title.lower() or
                "serverless" in session.abstract.lower() or
                "lambda" in session.title.lower() or
                "lambda" in session.abstract.lower() or
                any("serverless" in topic.lower() or "lambda" in topic.lower() for topic in session.topics)
            )
            assert found
    
    def test_search_sessions_get_sessions_by_short_id(self):
        """Test retrieving sessions by short_id (case-insensitive)"""
        repo = SessionRepositoryMock()
        sessions = repo.get_sessions_by_short_id("TNC301")
        
        assert len(sessions) == 1
        assert sessions[0].short_id == "TNC301"
    
    def test_search_sessions_get_sessions_by_short_id_case_insensitive(self):
        """Test short_id search is case-insensitive"""
        repo = SessionRepositoryMock()
        
        sessions_upper = repo.get_sessions_by_short_id("TNC301")
        sessions_lower = repo.get_sessions_by_short_id("tnc301")
        sessions_mixed = repo.get_sessions_by_short_id("TnC301")
        
        assert len(sessions_upper) == 1
        assert len(sessions_lower) == 1
        assert len(sessions_mixed) == 1
        assert sessions_upper[0].session_id == sessions_lower[0].session_id
        assert sessions_upper[0].session_id == sessions_mixed[0].session_id
