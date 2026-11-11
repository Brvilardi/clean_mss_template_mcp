from .get_sessions_by_level_controller import GetSessionsByLevelController
from .get_sessions_by_level_usecase import GetSessionsByLevelUsecase
from src.shared.environments import Environments
from src.shared.helpers.external_interfaces.http_lambda_requests import LambdaHttpRequest, LambdaHttpResponse

repo = Environments.get_session_repo()()
usecase = GetSessionsByLevelUsecase(repo)
controller = GetSessionsByLevelController(usecase)

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
