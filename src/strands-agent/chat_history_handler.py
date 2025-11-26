"""
BFF Lambda handler for retrieving chat history.

This module provides a Backend-for-Frontend (BFF) Lambda function for the chat frontend.

Supports two modes:
1. GET /sessions - Returns empty list (AgentCore Memory doesn't support listing all sessions)
2. GET /sessions?session_id=xxx - Returns events/messages for a specific session
"""

import json
import os
import boto3
from typing import Dict, Any, List
from datetime import datetime
from decimal import Decimal
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

# Initialize Powertools
logger = Logger(service="chat-history")
tracer = Tracer(service="chat-history")
metrics = Metrics(namespace="StrandsAgent", service="chat-history")


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime and Decimal objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def parse_event_payload(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and simplify AgentCore Memory event payload for frontend consumption.
    
    Extracts the actual message content from nested JSON strings and structures
    it in a clean, easy-to-render format.
    
    Args:
        event: Raw event from AgentCore Memory
        
    Returns:
        Simplified event structure with parsed content
    """
    try:
        simplified_event = {
            "event_id": event.get("eventId"),
            "timestamp": event.get("eventTimestamp"),
            "type": "unknown",
            "role": "unknown",
            "content": None
        }
        
        # Extract payload
        payload = event.get("payload", [])
        if not payload or len(payload) == 0:
            return simplified_event
        
        first_payload = payload[0]
        
        # Handle conversational events
        if "conversational" in first_payload:
            conversational = first_payload["conversational"]
            simplified_event["role"] = conversational.get("role", "unknown").lower()
            
            # Parse the nested JSON content
            content = conversational.get("content", {})
            text_content = content.get("text", "")
            
            if text_content:
                try:
                    # Parse the JSON string to get the actual message
                    message_data = json.loads(text_content)
                    message = message_data.get("message", {})
                    message_content = message.get("content", [])
                    
                    # Extract text or tool use from content
                    if message_content:
                        for item in message_content:
                            if "text" in item:
                                simplified_event["type"] = "text"
                                simplified_event["content"] = item["text"]
                                break
                            elif "toolUse" in item:
                                simplified_event["type"] = "tool_use"
                                tool_use = item["toolUse"]
                                simplified_event["content"] = {
                                    "tool_name": tool_use.get("name"),
                                    "tool_input": tool_use.get("input")
                                }
                                break
                            elif "toolResult" in item:
                                simplified_event["type"] = "tool_result"
                                tool_result = item["toolResult"]
                                simplified_event["content"] = {
                                    "tool_use_id": tool_result.get("toolUseId"),
                                    "status": tool_result.get("status"),
                                    "result": tool_result.get("content", [{}])[0].get("text") if tool_result.get("content") else None
                                }
                                break
                except json.JSONDecodeError:
                    # If parsing fails, use the raw text
                    simplified_event["type"] = "text"
                    simplified_event["content"] = text_content
        
        # Handle blob events (tool results)
        elif "blob" in first_payload:
            simplified_event["type"] = "blob"
            simplified_event["role"] = "user"
            blob_content = first_payload["blob"]
            
            try:
                # Try to parse blob as JSON
                parsed_blob = json.loads(blob_content)
                simplified_event["content"] = parsed_blob
            except (json.JSONDecodeError, TypeError):
                simplified_event["content"] = blob_content
        
        return simplified_event
        
    except Exception as e:
        logger.warning(f"Error parsing event payload: {str(e)}", extra={"event_id": event.get("eventId")})
        # Return a safe fallback
        return {
            "event_id": event.get("eventId"),
            "timestamp": event.get("eventTimestamp"),
            "type": "error",
            "role": "system",
            "content": "Error parsing event"
        }


@tracer.capture_method
def get_session_events(
    memory_id: str, actor_id: str, session_id: str, region: str
) -> List[Dict[str, Any]]:
    """
    Fetch events for a specific session from AgentCore Memory.
    
    Args:
        memory_id: AgentCore Memory ID
        actor_id: User identifier
        session_id: Session identifier
        region: AWS region
        
    Returns:
        List of event dictionaries
    """
    client = boto3.client("bedrock-agentcore", region_name=region)
    events = []
    next_token = None
    page_count = 0

    logger.info(
        "Fetching events from AgentCore Memory",
        extra={
            "memory_id": memory_id,
            "actor_id": actor_id,
            "session_id": session_id
        }
    )

    try:
        while True:
            page_count += 1
            params = {
                "memoryId": memory_id,
                "actorId": actor_id,
                "sessionId": session_id,
                "includePayloads": True,
                "maxResults": 100,
            }
            if next_token:
                params["nextToken"] = next_token

            logger.debug(f"Fetching page {page_count}")
            response = client.list_events(**params)
            page_events = response.get("events", [])
            events.extend(page_events)
            
            logger.debug(f"Page {page_count}: Retrieved {len(page_events)} events")
            metrics.add_metric(name="EventsRetrieved", unit=MetricUnit.Count, value=len(page_events))

            next_token = response.get("nextToken")
            if not next_token:
                break

        logger.info(
            "Successfully retrieved events",
            extra={
                "total_events": len(events),
                "pages_fetched": page_count,
                "session_id": session_id
            }
        )

        logger.info(
            "Events retrieved",
            extra={
                "total_events": len(events),
                "events": events,
            }
        )
        
        metrics.add_metric(name="TotalEventsRetrieved", unit=MetricUnit.Count, value=len(events))
        metrics.add_metric(name="PagesFetched", unit=MetricUnit.Count, value=page_count)
        
        # Log event summary
        if events:
            event_types = {}
            for event in events:
                event_type = event.get("eventType", "unknown")
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            logger.debug(
                "Event type distribution",
                extra={"event_types": event_types}
            )

        return events

    except Exception as e:
        logger.exception(
            "Error fetching events",
            extra={
                "session_id": session_id,
                "actor_id": actor_id,
                "memory_id": memory_id
            }
        )
        metrics.add_metric(name="EventFetchErrors", unit=MetricUnit.Count, value=1)
        raise


@tracer.capture_method
def get_chat_history(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get chat history or events for a specific session.
    
    Query Parameters:
        session_id (optional): If provided, returns events for that session
        
    Returns:
        - Without session_id: Empty sessions list with guidance
        - With session_id: Events/messages for that session
    """
    try:
        # Extract actor_id from JWT token
        request_context = event.get("requestContext", {})
        authorizer = request_context.get("authorizer", {})
        claims = authorizer.get("claims", {})
        
        # Use cognito:username instead of sub for consistency with agent
        actor_id = claims.get("cognito:username") or claims.get("sub")
        user_email = claims.get("email", "unknown")
        
        logger.info(
            "Processing chat history request",
            extra={
                "actor_id": actor_id,
                "user_email": user_email,
                "has_username": bool(claims.get("cognito:username")),
                "has_sub": bool(claims.get("sub"))
            }
        )

        if not actor_id:
            logger.warning("Unauthorized request - no actor_id found in claims")
            metrics.add_metric(name="UnauthorizedRequests", unit=MetricUnit.Count, value=1)
            return {
                "statusCode": 401,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(
                    {
                        "error": "Unauthorized",
                        "message": "Unable to identify user from authentication token",
                    }
                ),
            }

        # Check for session_id query parameter
        query_params = event.get("queryStringParameters") or {}
        session_id = query_params.get("session_id")

        logger.debug(
            "Request details",
            extra={
                "query_params": query_params,
                "session_id": session_id,
                "actor_id": actor_id
            }
        )

        # If session_id provided, fetch events for that session
        if session_id:
            metrics.add_metric(name="SessionHistoryRequests", unit=MetricUnit.Count, value=1)
            
            memory_id = os.getenv("MEMORY_ID")
            aws_region = os.getenv("AWS_REGION", "us-east-1")

            if not memory_id:
                logger.error("MEMORY_ID environment variable not set")
                metrics.add_metric(name="ConfigurationErrors", unit=MetricUnit.Count, value=1)
                return {
                    "statusCode": 500,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "body": json.dumps(
                        {
                            "error": "Internal server error",
                            "message": "Service configuration error",
                        }
                    ),
                }

            try:
                raw_events = get_session_events(memory_id, actor_id, session_id, aws_region)
                
                # Parse and simplify events for frontend
                parsed_events = [parse_event_payload(event) for event in raw_events]

                response_data = {
                    "session_id": session_id,
                    "actor_id": actor_id,
                    "events": parsed_events,
                    "event_count": len(parsed_events),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
                
                logger.info(
                    "Successfully retrieved and parsed session events",
                    extra={
                        "session_id": session_id,
                        "event_count": len(parsed_events)
                    }
                )
                metrics.add_metric(name="SuccessfulRequests", unit=MetricUnit.Count, value=1)

                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "body": json.dumps(response_data, cls=DateTimeEncoder),
                }

            except Exception as e:
                error_msg = str(e)
                logger.exception(
                    "Error fetching session events",
                    extra={
                        "session_id": session_id,
                        "actor_id": actor_id,
                        "memory_id": memory_id
                    }
                )
                metrics.add_metric(name="FailedRequests", unit=MetricUnit.Count, value=1)
                
                return {
                    "statusCode": 500,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "body": json.dumps(
                        {
                            "error": "Failed to fetch session events",
                            "message": error_msg,
                            "session_id": session_id,
                        },
                        cls=DateTimeEncoder
                    ),
                }

        # No session_id - return empty list with guidance
        logger.info("No session_id provided - returning guidance")
        metrics.add_metric(name="ListSessionsRequests", unit=MetricUnit.Count, value=1)
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "sessions": [],
                    "count": 0,
                    "actor_id": actor_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "message": "To get session events, provide session_id query parameter: /sessions?session_id=xxx",
                },
                cls=DateTimeEncoder
            ),
        }

    except Exception as e:
        error_msg = str(e)
        logger.exception("Unexpected error in get_chat_history")
        metrics.add_metric(name="UnexpectedErrors", unit=MetricUnit.Count, value=1)
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": "Internal server error", "message": error_msg}, cls=DateTimeEncoder),
        }


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda handler for API Gateway requests.
    
    This handler is protected by API Gateway Cognito User Pool authorizer.
    The authorizer validates the JWT token before this function is invoked.
    
    Args:
        event: API Gateway event with requestContext.authorizer.claims populated by Cognito
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    # Check HTTP method
    http_method = event.get(
        "httpMethod", event.get("requestContext", {}).get("http", {}).get("method", "GET")
    )
    
    logger.info(f"Received {http_method} request")
    metrics.add_metric(name="Invocations", unit=MetricUnit.Count, value=1)

    if http_method == "GET":
        return get_chat_history(event)
    else:
        logger.warning(f"Method not allowed: {http_method}")
        metrics.add_metric(name="MethodNotAllowed", unit=MetricUnit.Count, value=1)
        return {
            "statusCode": 405,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "error": "Method not allowed",
                    "message": f"HTTP method {http_method} is not supported. Only GET is allowed.",
                }
            ),
        }
