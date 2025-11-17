from .get_sessions_by_venue_controller import GetSessionsByVenueController
from .get_sessions_by_venue_usecase import GetSessionsByVenueUsecase
from src.shared.environments import Environments
from src.shared.helpers.external_interfaces.http_lambda_requests import LambdaHttpRequest, LambdaHttpResponse

repo = Environments.get_session_repo()()
usecase = GetSessionsByVenueUsecase(repo)
controller = GetSessionsByVenueController(usecase)

def lambda_handler(event, context):
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
