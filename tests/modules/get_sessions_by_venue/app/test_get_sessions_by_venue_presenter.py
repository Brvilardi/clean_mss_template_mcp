import json
from src.modules.get_sessions_by_venue.app.get_sessions_by_venue_presenter import lambda_handler


class Test_GetSessionsByVenuePresenter:
    def test_get_sessions_by_venue(self):
        """Test Lambda handler with valid event using query parameters"""
        event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/get-sessions-by-venue",
            "rawQueryString": "venue_name=Mandalay%20Bay",
            "headers": {
                "header1": "value1"
            },
            "queryStringParameters": {
                "venue_name": "Mandalay Bay"
            },
            "requestContext": {
                "accountId": "123456789012",
                "apiId": "<urlid>",
                "domainName": "<url-id>.lambda-url.us-west-2.on.aws",
                "http": {
                    "method": "GET",
                    "path": "/get-sessions-by-venue",
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
        assert "venue_name" in body
        assert body["venue_name"] == "Mandalay Bay"
