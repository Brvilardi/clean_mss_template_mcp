import pytest
import time
from src.shared.infra.pagination.dynamodb_pagination_helper import DynamoDBPaginationHelper


class Test_DynamoDBPaginationHelper:
    
    def test_encode_last_evaluated_key_with_simple_key(self):
        """Test encoding a simple DynamoDB LastEvaluatedKey"""
        helper = DynamoDBPaginationHelper()
        last_evaluated_key = {
            'PK': 'SESSION#123',
            'SK': '2025-12-04T21:00:00.000Z'
        }
        
        token = helper.encode_last_evaluated_key(last_evaluated_key)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_encode_last_evaluated_key_with_gsi_keys(self):
        """Test encoding DynamoDB key with GSI attributes"""
        helper = DynamoDBPaginationHelper()
        last_evaluated_key = {
            'PK': 'SESSION#456',
            'SK': '2025-12-05T09:00:00.000Z',
            'GSI1PK': 'VENUE#Mandalay Bay',
            'GSI1SK': '2025-12-05T09:00:00.000Z'
        }
        
        token = helper.encode_last_evaluated_key(last_evaluated_key)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_encode_last_evaluated_key_with_custom_ttl(self):
        """Test encoding with custom TTL"""
        helper = DynamoDBPaginationHelper()
        last_evaluated_key = {'PK': 'SESSION#789', 'SK': 'test'}
        
        token = helper.encode_last_evaluated_key(last_evaluated_key, ttl_seconds=600)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_decode_to_exclusive_start_key_with_valid_token(self):
        """Test decoding a valid token to ExclusiveStartKey"""
        helper = DynamoDBPaginationHelper()
        last_evaluated_key = {
            'PK': 'SESSION#123',
            'SK': '2025-12-04T21:00:00.000Z'
        }
        
        token = helper.encode_last_evaluated_key(last_evaluated_key)
        exclusive_start_key = helper.decode_to_exclusive_start_key(token)
        
        assert exclusive_start_key == last_evaluated_key
    
    def test_decode_to_exclusive_start_key_removes_ttl_metadata(self):
        """Test that TTL metadata is removed from ExclusiveStartKey"""
        helper = DynamoDBPaginationHelper()
        last_evaluated_key = {
            'PK': 'SESSION#456',
            'SK': '2025-12-05T09:00:00.000Z'
        }
        
        token = helper.encode_last_evaluated_key(last_evaluated_key)
        exclusive_start_key = helper.decode_to_exclusive_start_key(token)
        
        assert 'issued_at' not in exclusive_start_key
        assert 'ttl' not in exclusive_start_key
        assert exclusive_start_key == last_evaluated_key
    
    def test_decode_to_exclusive_start_key_with_expired_token(self):
        """Test decoding an expired token raises ValueError"""
        helper = DynamoDBPaginationHelper()
        last_evaluated_key = {'PK': 'SESSION#789', 'SK': 'test'}
        
        # Create token with very short TTL
        token = helper.encode_last_evaluated_key(last_evaluated_key, ttl_seconds=1)
        
        # Wait for token to expire
        time.sleep(2)
        
        with pytest.raises(ValueError) as exc_info:
            helper.decode_to_exclusive_start_key(token, max_age_seconds=1)
        
        assert "Pagination token expired" in str(exc_info.value)
    
    def test_decode_to_exclusive_start_key_with_invalid_token(self):
        """Test decoding invalid token raises ValueError"""
        helper = DynamoDBPaginationHelper()
        invalid_token = "not-valid-base64!!!"
        
        with pytest.raises(ValueError) as exc_info:
            helper.decode_to_exclusive_start_key(invalid_token)
        
        assert "Invalid pagination token" in str(exc_info.value)
    
    def test_validate_page_size_with_valid_values(self):
        """Test validate_page_size with valid values"""
        helper = DynamoDBPaginationHelper()
        assert helper.validate_page_size(1) == 1
        assert helper.validate_page_size(50) == 50
        assert helper.validate_page_size(100) == 100
    
    def test_validate_page_size_with_none_returns_default(self):
        """Test validate_page_size with None returns default 50"""
        helper = DynamoDBPaginationHelper()
        assert helper.validate_page_size(None) == 50
    
    def test_validate_page_size_with_invalid_values(self):
        """Test validate_page_size with invalid values raises ValueError"""
        helper = DynamoDBPaginationHelper()
        
        with pytest.raises(ValueError):
            helper.validate_page_size(0)
        
        with pytest.raises(ValueError):
            helper.validate_page_size(101)
        
        with pytest.raises(ValueError):
            helper.validate_page_size("abc")
    
    def test_round_trip_dynamodb_keys(self):
        """Test round-trip encoding and decoding preserves DynamoDB keys"""
        helper = DynamoDBPaginationHelper()
        original_key = {
            'PK': 'SESSION#999',
            'SK': '2025-12-06T15:30:00.000Z',
            'GSI1PK': 'VENUE#Venetian',
            'GSI1SK': '2025-12-06T15:30:00.000Z'
        }
        
        # Encode
        token = helper.encode_last_evaluated_key(original_key)
        
        # Decode
        decoded_key = helper.decode_to_exclusive_start_key(token)
        
        # Verify all original fields are preserved
        assert decoded_key == original_key
    
    def test_round_trip_with_custom_ttl(self):
        """Test round-trip with custom TTL preserves data"""
        helper = DynamoDBPaginationHelper()
        original_key = {'PK': 'SESSION#111', 'SK': 'test'}
        
        token = helper.encode_last_evaluated_key(original_key, ttl_seconds=600)
        decoded_key = helper.decode_to_exclusive_start_key(token, max_age_seconds=600)
        
        assert decoded_key == original_key
