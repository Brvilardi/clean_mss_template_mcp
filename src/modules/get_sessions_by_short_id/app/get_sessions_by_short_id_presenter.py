from .get_sessions_by_short_id_controller import GetSessionsByShortIdController
from .get_sessions_by_short_id_usecase import GetSessionsByShortIdUsecase
from src.shared.environments import Environments
from src.shared.helpers.external_interfaces.http_lambda_requests import LambdaHttpRequest, LambdaHttpResponse

repo = Environments.get_session_repo()()
usecase = GetSessionsByShortIdUsecase(repo)
controller = GetSessionsByShortIdController(usecase)

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
