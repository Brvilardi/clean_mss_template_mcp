from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class IPaginationHelper(ABC):
    """
    Interface for pagination token handling.
    
    Defines methods for encoding/decoding pagination tokens with TTL support.
    Implementations should be database-agnostic at this level.
    """
    
    @abstractmethod
    def encode_token(self, cursor_data: Dict[str, Any], ttl_seconds: Optional[int] = None) -> str:
        """
        Encodes cursor data to a pagination token string with TTL.
        
        Args:
            cursor_data: Database-agnostic cursor data
            ttl_seconds: Time-to-live in seconds
            
        Returns:
            Encoded pagination token string
        """
        pass
    
    @abstractmethod
    def decode_token(self, token: str, max_age_seconds: Optional[int] = None) -> Dict[str, Any]:
        """
        Decodes and validates pagination token with TTL check.
        
        Args:
            token: Encoded pagination token
            max_age_seconds: Maximum age in seconds
            
        Returns:
            Decoded cursor data
            
        Raises:
            ValueError: If token is expired or invalid
        """
        pass
    
    @abstractmethod
    def validate_page_size(self, page_size: Optional[int]) -> int:
        """
        Validates and returns page size with default.
        
        Args:
            page_size: Requested page size
            
        Returns:
            Validated page size
            
        Raises:
            ValueError: If page_size is invalid
        """
        pass
