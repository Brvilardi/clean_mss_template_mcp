from src.shared.helpers.external_interfaces.external_interface import IResponse, IRequest
from .get_sessions_by_short_id_usecase import GetSessionsByShortIdUsecase
from .get_sessions_by_short_id_viewmodel import GetSessionsByShortIdViewmodel
from src.shared.helpers.errors.controller_errors import MissingParameters
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.helpers.external_interfaces.http_codes import OK, BadRequest, InternalServerError


class GetSessionsByShortIdController:
    
    def __init__(self, usecase: GetSessionsByShortIdUsecase):
        self.GetSessionsByShortIdUsecase = usecase
    
    def __call__(self, request: IRequest) -> IResponse:
        try:
            # Extract short_id from query parameters
            short_id = request.data.get('short_id')
            
            if short_id is None:
                raise MissingParameters('short_id')
            
            # Call use case
            sessions = self.GetSessionsByShortIdUsecase(short_id=short_id)
            
            # Create view model and return
            viewmodel = GetSessionsByShortIdViewmodel(sessions=sessions, short_id=short_id)
            return OK(viewmodel.to_dict())
        
        except MissingParameters as err:
            return BadRequest(body=err.message)
        except EntityError as err:
            return BadRequest(body=err.message)
        except Exception as err:
            return InternalServerError(body=err.args[0])
