import base64
import json
import time
from typing import Optional, Dict, Any
from .pagination_interface import IPaginationHelper


class PaginationHelper(IPaginationHelper):
    """
    Database-agnostic pagination helper with TTL support.
    
    Provides generic methods to encode/decode pagination tokens and validate page sizes.
    This implementation is not tied to any specific database technology.
    """
    
    # Default TTL for pagination tokens (5 minutes)
    DEFAULT_TOKEN_TTL_SECONDS = 300
    
    def encode_token(self, cursor_data: Dict[str, Any], ttl_seconds: Optional[int] = None) -> str:
        """
        Encodes cursor data to base64 string with TTL.
        
        Args:
            cursor_data: Database-agnostic cursor data
            ttl_seconds: Time-to-live in seconds (default 300 = 5 minutes)
            
        Returns:
            Base64-encoded string with embedded timestamp
        """
        if ttl_seconds is None:
            ttl_seconds = self.DEFAULT_TOKEN_TTL_SECONDS
        
        # Add timestamp and TTL to token
        token_data = {
            **cursor_data,
            'issued_at': int(time.time()),
            'ttl': ttl_seconds
        }
        
        json_str = json.dumps(token_data)
        encoded = base64.b64encode(json_str.encode('utf-8'))
        return encoded.decode('utf-8')
    
    def decode_token(self, token: str, max_age_seconds: Optional[int] = None) -> Dict[str, Any]:
        """
        Decodes and validates base64 pagination token with TTL check.
        
        Args:
            token: Base64-encoded pagination token
            max_age_seconds: Maximum age in seconds (default 300 = 5 minutes)
            
        Returns:
            Decoded cursor data (without TTL metadata)
            
        Raises:
            ValueError: If token is expired, invalid base64, or invalid JSON
        """
        if max_age_seconds is None:
            max_age_seconds = self.DEFAULT_TOKEN_TTL_SECONDS
        
        try:
            decoded = base64.b64decode(token.encode('utf-8'))
            token_data = json.loads(decoded.decode('utf-8'))
            
            # Check if token has TTL info and validate expiration
            if 'issued_at' in token_data:
                issued_at = token_data['issued_at']
                current_time = int(time.time())
                age = current_time - issued_at
                
                if age > max_age_seconds:
                    raise ValueError(
                        f"Pagination token expired. Tokens are valid for {max_age_seconds} seconds. "
                        f"Please restart pagination from the first page."
                    )
            
            # Remove TTL metadata and return only cursor data
            cursor_data = {k: v for k, v in token_data.items() if k not in ['issued_at', 'ttl']}
            return cursor_data
            
        except (ValueError, json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid pagination token: {str(e)}")
    
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
        if page_size is None:
            return 50  # Default page size
        
        if not isinstance(page_size, int):
            raise ValueError("page_size must be an integer")
        
        if page_size < 1:
            raise ValueError("page_size must be at least 1")
        
        if page_size > 100:
            raise ValueError("page_size cannot exceed 100")
        
        return page_size
