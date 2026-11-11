import pytest
import time
from src.shared.helpers.pagination.pagination_helper import PaginationHelper


class Test_PaginationHelper:
    
    def test_encode_token_with_simple_data(self):
        """Test encoding simple cursor data"""
        helper = PaginationHelper()
        cursor_data = {
            'id': '123',
            'timestamp': '2025-12-04T21:00:00.000Z'
        }
        
        token = helper.encode_token(cursor_data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_encode_token_with_complex_data(self):
        """Test encoding complex cursor data with multiple attributes"""
        helper = PaginationHelper()
        cursor_data = {
            'id': '456',
            'timestamp': '2025-12-05T09:00:00.000Z',
            'category': 'test',
            'sort_key': 'value'
        }
        
        token = helper.encode_token(cursor_data)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_encode_token_with_custom_ttl(self):
        """Test encoding with custom TTL"""
        helper = PaginationHelper()
        cursor_data = {'id': '789', 'key': 'test'}
        
        token = helper.encode_token(cursor_data, ttl_seconds=600)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_decode_token_with_valid_token(self):
        """Test decoding a valid token"""
        helper = PaginationHelper()
        cursor_data = {
            'id': '123',
            'timestamp': '2025-12-04T21:00:00.000Z'
        }
        
        token = helper.encode_token(cursor_data)
        decoded = helper.decode_token(token)
        
        assert decoded == cursor_data
    
    def test_decode_token_removes_ttl_metadata(self):
        """Test that TTL metadata is removed from decoded token"""
        helper = PaginationHelper()
        cursor_data = {
            'id': '456',
            'timestamp': '2025-12-05T09:00:00.000Z'
        }
        
        token = helper.encode_token(cursor_data)
        decoded = helper.decode_token(token)
        
        assert 'issued_at' not in decoded
        assert 'ttl' not in decoded
        assert decoded == cursor_data
    
    def test_decode_token_with_expired_token(self):
        """Test decoding an expired token raises ValueError"""
        helper = PaginationHelper()
        cursor_data = {'id': '789', 'key': 'test'}
        
        # Create token with very short TTL
        token = helper.encode_token(cursor_data, ttl_seconds=1)
        
        # Wait for token to expire
        time.sleep(2)
        
        with pytest.raises(ValueError) as exc_info:
            helper.decode_token(token, max_age_seconds=1)
        
        assert "Pagination token expired" in str(exc_info.value)
        assert "Tokens are valid for 1 seconds" in str(exc_info.value)
    
    def test_decode_token_with_invalid_base64(self):
        """Test decoding invalid base64 raises ValueError"""
        helper = PaginationHelper()
        invalid_token = "not-valid-base64!!!"
        
        with pytest.raises(ValueError) as exc_info:
            helper.decode_token(invalid_token)
        
        assert "Invalid pagination token" in str(exc_info.value)
    
    def test_decode_token_with_invalid_json(self):
        """Test decoding token with invalid JSON raises ValueError"""
        helper = PaginationHelper()
        import base64
        invalid_json = base64.b64encode(b"not valid json").decode('utf-8')
        
        with pytest.raises(ValueError) as exc_info:
            helper.decode_token(invalid_json)
        
        assert "Invalid pagination token" in str(exc_info.value)
    
    def test_validate_page_size_with_valid_values(self):
        """Test validate_page_size with valid values"""
        helper = PaginationHelper()
        assert helper.validate_page_size(1) == 1
        assert helper.validate_page_size(50) == 50
        assert helper.validate_page_size(100) == 100
        assert helper.validate_page_size(25) == 25
    
    def test_validate_page_size_with_none_returns_default(self):
        """Test validate_page_size with None returns default 50"""
        helper = PaginationHelper()
        assert helper.validate_page_size(None) == 50
    
    def test_validate_page_size_with_zero_raises_error(self):
        """Test validate_page_size with 0 raises ValueError"""
        helper = PaginationHelper()
        with pytest.raises(ValueError) as exc_info:
            helper.validate_page_size(0)
        
        assert "page_size must be at least 1" in str(exc_info.value)
    
    def test_validate_page_size_with_negative_raises_error(self):
        """Test validate_page_size with negative value raises ValueError"""
        helper = PaginationHelper()
        with pytest.raises(ValueError) as exc_info:
            helper.validate_page_size(-1)
        
        assert "page_size must be at least 1" in str(exc_info.value)
    
    def test_validate_page_size_with_over_100_raises_error(self):
        """Test validate_page_size with value over 100 raises ValueError"""
        helper = PaginationHelper()
        with pytest.raises(ValueError) as exc_info:
            helper.validate_page_size(101)
        
        assert "page_size cannot exceed 100" in str(exc_info.value)
    
    def test_validate_page_size_with_string_raises_error(self):
        """Test validate_page_size with string raises ValueError"""
        helper = PaginationHelper()
        with pytest.raises(ValueError) as exc_info:
            helper.validate_page_size("abc")
        
        assert "page_size must be an integer" in str(exc_info.value)
    
    def test_validate_page_size_with_float_raises_error(self):
        """Test validate_page_size with float raises ValueError"""
        helper = PaginationHelper()
        with pytest.raises(ValueError) as exc_info:
            helper.validate_page_size(50.5)
        
        assert "page_size must be an integer" in str(exc_info.value)
    
    def test_round_trip_encoding_decoding(self):
        """Test round-trip encoding and decoding preserves data"""
        helper = PaginationHelper()
        original_data = {
            'id': '999',
            'timestamp': '2025-12-06T15:30:00.000Z',
            'category': 'test',
            'sort_key': 'value'
        }
        
        # Encode
        token = helper.encode_token(original_data)
        
        # Decode
        decoded_data = helper.decode_token(token)
        
        # Verify all original fields are preserved
        assert decoded_data == original_data
    
    def test_round_trip_with_custom_ttl(self):
        """Test round-trip with custom TTL preserves data"""
        helper = PaginationHelper()
        original_data = {'id': '111', 'key': 'test'}
        
        token = helper.encode_token(original_data, ttl_seconds=600)
        decoded_data = helper.decode_token(token, max_age_seconds=600)
        
        assert decoded_data == original_data
    
    def test_default_ttl_constant(self):
        """Test that DEFAULT_TOKEN_TTL_SECONDS is set correctly"""
        assert PaginationHelper.DEFAULT_TOKEN_TTL_SECONDS == 300
