import json
from src.modules.get_all_sessions_paginated.app.get_all_sessions_paginated_presenter import lambda_handler


class Test_GetAllSessionsPaginatedPresenter:
    def test_lambda_handler_with_valid_event(self):
        """Test Lambda handler with valid event"""
        event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/sessions/paginated",
            "headers": {
                "header1": "value1"
            },
            "queryStringParameters": {
                "page_size": "2"
            },
            "requestContext": {
                "accountId": "123456789012",
                "apiId": "<urlid>",
                "domainName": "<url-id>.lambda-url.us-west-2.on.aws",
                "http": {
                    "method": "GET",
                    "path": "/sessions/paginated",
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
        
        response = lambda_handler(event, None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "sessions" in body
        assert "count" in body
        assert "page_size" in body
        assert "has_more" in body
    
    def test_response_status_code_is_200(self):
        """Test response status code is 200"""
        event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/sessions/paginated",
            "queryStringParameters": {
                "page_size": "3"
            },
            "requestContext": {
                "http": {
                    "method": "GET"
                }
            }
        }
        
        response = lambda_handler(event, None)
        
        assert response["statusCode"] == 200
    
    def test_response_body_includes_pagination_metadata(self):
        """Test response body includes pagination metadata"""
        event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/sessions/paginated",
            "queryStringParameters": {
                "page_size": "2"
            },
            "requestContext": {
                "http": {
                    "method": "GET"
                }
            }
        }
        
        response = lambda_handler(event, None)
        
        body = json.loads(response["body"])
        assert "sessions" in body
        assert "count" in body
        assert "page_size" in body
        assert "has_more" in body
        assert body["page_size"] == 2
