from typing import Optional, Dict, Any
from src.shared.helpers.pagination.pagination_helper import PaginationHelper


class DynamoDBPaginationHelper:
    """
    DynamoDB-specific pagination helper.
    
    Wraps the generic PaginationHelper to provide DynamoDB-specific
    token encoding/decoding for LastEvaluatedKey and ExclusiveStartKey.
    """
    
    def __init__(self):
        self.pagination_helper = PaginationHelper()
    
    def encode_last_evaluated_key(self, last_evaluated_key: Dict[str, Any], ttl_seconds: Optional[int] = None) -> str:
        """
        Encodes DynamoDB LastEvaluatedKey to pagination token.
        
        Args:
            last_evaluated_key: DynamoDB LastEvaluatedKey dict
            ttl_seconds: Time-to-live in seconds
            
        Returns:
            Base64-encoded pagination token
        """
        return self.pagination_helper.encode_token(last_evaluated_key, ttl_seconds)
    
    def decode_to_exclusive_start_key(self, token: str, max_age_seconds: Optional[int] = None) -> Dict[str, Any]:
        """
        Decodes pagination token to DynamoDB ExclusiveStartKey.
        
        Args:
            token: Base64-encoded pagination token
            max_age_seconds: Maximum age in seconds
            
        Returns:
            DynamoDB ExclusiveStartKey dict
            
        Raises:
            ValueError: If token is expired or invalid
        """
        return self.pagination_helper.decode_token(token, max_age_seconds)
    
    def validate_page_size(self, page_size: Optional[int]) -> int:
        """
        Validates and returns page size with default.
        
        Args:
            page_size: Requested page size
            
        Returns:
            Validated page size (default 50 if None)
            
        Raises:
            ValueError: If page_size is invalid
        """
        return self.pagination_helper.validate_page_size(page_size)
