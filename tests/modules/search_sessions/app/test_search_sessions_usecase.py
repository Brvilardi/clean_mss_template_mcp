import pytest
from src.modules.search_sessions.app.search_sessions_usecase import SearchSessionsUsecase
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_SearchSessionsUsecase:
    
    def test_search_sessions_valid_filter_combinations(self):
        """Test search with valid filter combinations"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        # Test with all filters
        sessions, next_token = usecase(
            day="Monday",
            venue="Venetian",
            level=300,
            keywords="security",
            page_size=20
        )
        
        assert isinstance(sessions, list)
        assert next_token is None or isinstance(next_token, str)
    
    def test_search_sessions_invalid_day_raises_entity_error(self):
        """Test invalid day values raise EntityError"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        with pytest.raises(EntityError):
            usecase(day="InvalidDay")
    
    def test_search_sessions_invalid_level_raises_entity_error(self):
        """Test invalid level values raise EntityError"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        with pytest.raises(EntityError):
            usecase(level=500)
        
        with pytest.raises(EntityError):
            usecase(level=0)
        
        with pytest.raises(EntityError):
            usecase(level=150)
    
    def test_search_sessions_invalid_page_size_raises_entity_error(self):
        """Test invalid page_size values raise EntityError"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        # Test page_size < 1
        with pytest.raises(EntityError):
            usecase(page_size=0)
        
        # Test page_size > 100
        with pytest.raises(EntityError):
            usecase(page_size=101)
        
        # Test non-integer page_size
        with pytest.raises(EntityError):
            usecase(page_size="50")
    
    def test_search_sessions_default_page_size(self):
        """Test default page_size (50)"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        # Call without page_size parameter
        sessions, next_token = usecase()
        
        # The default should be 50, but we can't directly test it here
        # We verify the call succeeds with default
        assert isinstance(sessions, list)
    
    def test_search_sessions_maximum_page_size_enforcement(self):
        """Test maximum page_size enforcement (100)"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        # Test that page_size=100 is valid
        sessions, next_token = usecase(page_size=100)
        assert isinstance(sessions, list)
        
        # Test that page_size=101 raises error
        with pytest.raises(EntityError):
            usecase(page_size=101)
    
    def test_search_sessions_empty_filters(self):
        """Test empty filters"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        # Call with no filters
        sessions, next_token = usecase()
        
        assert isinstance(sessions, list)
        assert next_token is None or isinstance(next_token, str)
    
    def test_search_sessions_partial_filters(self):
        """Test with partial filters"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        # Test with only day
        sessions, next_token = usecase(day="Monday")
        assert isinstance(sessions, list)
        
        # Test with only venue
        sessions, next_token = usecase(venue="Venetian")
        assert isinstance(sessions, list)
        
        # Test with only level
        sessions, next_token = usecase(level=200)
        assert isinstance(sessions, list)
        
        # Test with only keywords
        sessions, next_token = usecase(keywords="machine learning")
        assert isinstance(sessions, list)
    
    def test_search_sessions_invalid_venue_empty_string(self):
        """Test invalid venue (empty string) raises EntityError"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        with pytest.raises(EntityError):
            usecase(venue="")
        
        with pytest.raises(EntityError):
            usecase(venue="   ")
    
    def test_search_sessions_valid_days(self):
        """Test all valid day values"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day in valid_days:
            sessions, next_token = usecase(day=day)
            assert isinstance(sessions, list)
    
    def test_search_sessions_valid_levels(self):
        """Test all valid level values"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        valid_levels = [100, 200, 300, 400]
        
        for level in valid_levels:
            sessions, next_token = usecase(level=level)
            assert isinstance(sessions, list)
    
    def test_search_sessions_invalid_speaker_empty_string(self):
        """Test invalid speaker (empty string) raises EntityError"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        with pytest.raises(EntityError):
            usecase(speaker="")
    
    def test_search_sessions_invalid_speaker_whitespace_only(self):
        """Test invalid speaker (whitespace-only) raises EntityError"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        with pytest.raises(EntityError):
            usecase(speaker="   ")
        
        with pytest.raises(EntityError):
            usecase(speaker="\t\n")
    
    def test_search_sessions_valid_speaker(self):
        """Test valid speaker parameter"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        sessions, next_token = usecase(speaker="John Doe")
        assert isinstance(sessions, list)
        assert next_token is None or isinstance(next_token, str)
    
    def test_search_sessions_speaker_with_other_filters(self):
        """Test speaker combined with other filters"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        sessions, next_token = usecase(
            speaker="John",
            day="Monday",
            venue="Venetian",
            level=300
        )
        assert isinstance(sessions, list)
        assert next_token is None or isinstance(next_token, str)
