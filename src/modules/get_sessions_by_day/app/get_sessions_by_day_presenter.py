from .get_sessions_by_day_controller import GetSessionsByDayController
from .get_sessions_by_day_usecase import GetSessionsByDayUsecase
from src.shared.environments import Environments
from src.shared.helpers.external_interfaces.http_lambda_requests import LambdaHttpRequest, LambdaHttpResponse

repo = Environments.get_session_repo()()
usecase = GetSessionsByDayUsecase(repo)
controller = GetSessionsByDayController(usecase)

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
