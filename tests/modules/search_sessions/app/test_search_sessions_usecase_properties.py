import pytest
from hypothesis import given, strategies as st
from src.modules.search_sessions.app.search_sessions_usecase import SearchSessionsUsecase
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_SearchSessionsUsecase_Properties:
    
    @given(
        invalid_day=st.text().filter(
            lambda x: x not in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        )
    )
    def test_property_invalid_filter_rejection_day(self, invalid_day):
        """
        Feature: intelligent-session-search, Property 3: Invalid filter rejection
        Validates: Requirements 1.4
        
        For any invalid filter value (invalid day name), the search should raise EntityError.
        """
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        with pytest.raises(EntityError):
            usecase(day=invalid_day)
    
    @given(
        invalid_level=st.integers().filter(lambda x: x not in [100, 200, 300, 400])
    )
    def test_property_invalid_filter_rejection_level(self, invalid_level):
        """
        Feature: intelligent-session-search, Property 3: Invalid filter rejection
        Validates: Requirements 1.4
        
        For any invalid filter value (invalid level value), the search should raise EntityError.
        """
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        with pytest.raises(EntityError):
            usecase(level=invalid_level)
    
    @given(
        invalid_page_size=st.one_of(
            st.integers().filter(lambda x: x < 1 or x > 100),
            st.text(),
            st.floats(),
            st.none()
        )
    )
    def test_property_invalid_filter_rejection_page_size(self, invalid_page_size):
        """
        Feature: intelligent-session-search, Property 3: Invalid filter rejection
        Validates: Requirements 1.4
        
        For any invalid page_size value (not 1-100 or not an integer), the search should raise EntityError.
        """
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        with pytest.raises(EntityError):
            usecase(page_size=invalid_page_size)
    
    @given(
        invalid_venue=st.one_of(
            st.just(""),
            st.just("   "),
            st.integers(),
            st.floats()
        )
    )
    def test_property_invalid_filter_rejection_venue(self, invalid_venue):
        """
        Feature: intelligent-session-search, Property 3: Invalid filter rejection
        Validates: Requirements 1.4
        
        For any invalid venue value (empty string or non-string), the search should raise EntityError.
        """
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo)
        
        with pytest.raises(EntityError):
            usecase(venue=invalid_venue)
