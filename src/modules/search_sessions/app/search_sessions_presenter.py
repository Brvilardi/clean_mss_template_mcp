from .search_sessions_controller import SearchSessionsController
from .search_sessions_usecase import SearchSessionsUsecase
from src.shared.environments import Environments
from src.shared.helpers.external_interfaces.http_lambda_requests import LambdaHttpRequest, LambdaHttpResponse

repo = Environments.get_session_repo()()
usecase = SearchSessionsUsecase(repo)
controller = SearchSessionsController(usecase)

def lambda_handler(event, context):
    """
    Lambda handler for search sessions endpoint.
    
    Args:
        event: Lambda event containing query parameters
        context: Lambda context
        
    Returns:
        HTTP response with search results and pagination metadata
    """
    from pprint import pprint
    pprint(event)
    
    httpRequest = LambdaHttpRequest(data=event)
    response = controller(httpRequest)
    httpResponse = LambdaHttpResponse(
        status_code=response.status_code,
        body=response.body,
        headers=response.headers
    )
    
    return httpResponse.toDict()
