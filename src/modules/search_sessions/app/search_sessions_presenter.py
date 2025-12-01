from .search_sessions_controller import SearchSessionsController
from .search_sessions_usecase import SearchSessionsUsecase
from src.shared.environments import Environments
from src.shared.helpers.external_interfaces.http_lambda_requests import LambdaHttpRequest, LambdaHttpResponse
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging import correlation_paths

# Initialize Powertools
logger = Logger(service="search-sessions")
tracer = Tracer(service="search-sessions")

repo = Environments.get_session_repo()()
usecase = SearchSessionsUsecase(repo)
controller = SearchSessionsController(usecase)

@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    """
    Lambda handler for search sessions endpoint.
    
    Args:
        event: Lambda event containing query parameters
        context: Lambda context
        
    Returns:
        HTTP response with search results and pagination metadata
    """
    # Log incoming request with all parameters
    query_params = event.get('queryStringParameters', {}) or {}
    logger.info(
        "Search sessions request received",
        extra={
            "query_parameters": query_params,
            "has_pagination_token": 'next_page_token' in query_params
        }
    )
    
    httpRequest = LambdaHttpRequest(data=event)
    response = controller(httpRequest)
    
    # Log response summary
    if response.status_code == 200:
        body = response.body
        sessions_count = len(body.get('sessions', []))
        has_next_page = body.get('pagination', {}).get('next_page_token') is not None
        
        logger.info(
            "Search completed successfully",
            extra={
                "sessions_returned": sessions_count,
                "has_next_page": has_next_page,
                "status_code": response.status_code
            }
        )
        
        # Log session IDs for debugging
        if sessions_count > 0:
            session_ids = [s.get('short_id') for s in body.get('sessions', [])]
            logger.debug(
                "Sessions returned",
                extra={
                    "session_ids": session_ids,
                    "session_count": sessions_count
                }
            )
    else:
        logger.warning(
            "Search request failed",
            extra={
                "status_code": response.status_code,
                "error": response.body
            }
        )
    
    httpResponse = LambdaHttpResponse(
        status_code=response.status_code,
        body=response.body,
        headers=response.headers
    )
    
    return httpResponse.toDict()
