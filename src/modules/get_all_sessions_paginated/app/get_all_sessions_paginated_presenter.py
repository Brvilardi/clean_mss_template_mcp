from .get_all_sessions_paginated_controller import GetAllSessionsPaginatedController
from .get_all_sessions_paginated_usecase import GetAllSessionsPaginatedUsecase
from src.shared.environments import Environments
from src.shared.helpers.external_interfaces.http_lambda_requests import LambdaHttpRequest, LambdaHttpResponse

repo = Environments.get_session_repo()()
usecase = GetAllSessionsPaginatedUsecase(repo)
controller = GetAllSessionsPaginatedController(usecase)

def lambda_handler(event, context):
    """
    Lambda handler for get all sessions paginated endpoint.
    
    Args:
        event: Lambda event containing query parameters
        context: Lambda context
        
    Returns:
        HTTP response with paginated sessions
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
