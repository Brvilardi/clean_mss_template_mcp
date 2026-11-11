import json
from unittest.mock import Mock
from src.modules.search_sessions.app.search_sessions_presenter import lambda_handler


def create_mock_lambda_context():
    """Create a mock Lambda context for testing"""
    context = Mock()
    context.function_name = "test-search-sessions"
    context.memory_limit_in_mb = 128
    context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-search-sessions"
    context.aws_request_id = "test-request-id-123"
    return context


class Test_SearchSessionsPresenter:
    def test_lambda_handler_accepts_get_request(self):
        """Test Lambda handler accepts GET request event"""
        event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/sessions/search",
            "headers": {
                "header1": "value1"
            },
            "queryStringParameters": {
                "keywords": "security"
            },
            "requestContext": {
                "accountId": "123456789012",
                "apiId": "<urlid>",
                "domainName": "<url-id>.lambda-url.us-west-2.on.aws",
                "http": {
                    "method": "GET",
                    "path": "/sessions/search",
                    "protocol": "HTTP/1.1",
                    "sourceIp": "123.123.123.123",
                    "userAgent": "agent"
                },
                "requestId": "id",
                "routeKey": "$default",
                "stage": "$default",
                "time": "12/Mar/2020:19:03:58 +0000",
                "timeEpoch": 1583348638390
            },
            "isBase64Encoded": False
        }
        
        context = create_mock_lambda_context()
        response = lambda_handler(event, context)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "sessions" in body
        assert "pagination" in body
        assert "message" in body
    
    def test_query_parameters_extracted_correctly(self):
        """Test query parameters are extracted correctly"""
        event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/sessions/search",
            "queryStringParameters": {
                "day": "Monday",
                "venue": "Venetian",
                "level": "300",
                "keywords": "security machine learning",
                "page_size": "20"
            },
            "requestContext": {
                "http": {
                    "method": "GET"
                }
            }
        }
        
        context = create_mock_lambda_context()
        response = lambda_handler(event, context)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "sessions" in body
        assert "pagination" in body
        assert body["pagination"]["page_size"] <= 20
    
    def test_successful_response_format(self):
        """Test successful response format"""
        event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/sessions/search",
            "queryStringParameters": {
                "keywords": "AWS"
            },
            "requestContext": {
                "http": {
                    "method": "GET"
                }
            }
        }
        
        context = create_mock_lambda_context()
        response = lambda_handler(event, context)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "sessions" in body
        assert isinstance(body["sessions"], list)
        assert "pagination" in body
        assert "page_size" in body["pagination"]
        assert "next_page_token" in body["pagination"]
        assert "message" in body
        assert body["message"] == "search completed successfully"
    
    def test_endpoint_path_is_sessions_search(self):
        """Test endpoint path is /sessions/search"""
        event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/sessions/search",
            "queryStringParameters": {},
            "requestContext": {
                "http": {
                    "method": "GET",
                    "path": "/sessions/search"
                }
            }
        }
        
        context = create_mock_lambda_context()
        response = lambda_handler(event, context)
        
        # Verify the handler processes the request successfully
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "sessions" in body
    
    def test_empty_query_parameters(self):
        """Test with no query parameters returns all sessions"""
        event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/sessions/search",
            "queryStringParameters": None,
            "requestContext": {
                "http": {
                    "method": "GET"
                }
            }
        }
        
        context = create_mock_lambda_context()
        response = lambda_handler(event, context)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "sessions" in body
        assert isinstance(body["sessions"], list)
    
    def test_pagination_token_in_query_parameters(self):
        """Test next_page_token is extracted from query parameters"""
        event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/sessions/search",
            "queryStringParameters": {
                "page_size": "2",
                "next_page_token": "eyJQSyI6IlNFU1NJT04jYWJjMTIzIn0="
            },
            "requestContext": {
                "http": {
                    "method": "GET"
                }
            }
        }
        
        context = create_mock_lambda_context()
        response = lambda_handler(event, context)
        
        # Should process without error
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "sessions" in body
