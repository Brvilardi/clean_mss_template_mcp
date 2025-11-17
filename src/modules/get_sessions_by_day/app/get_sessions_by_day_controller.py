from src.shared.helpers.external_interfaces.external_interface import IResponse, IRequest
from .get_sessions_by_day_usecase import GetSessionsByDayUsecase
from .get_sessions_by_day_viewmodel import GetSessionsByDayViewmodel
from src.shared.helpers.errors.controller_errors import MissingParameters
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.helpers.external_interfaces.http_codes import OK, BadRequest, InternalServerError


class GetSessionsByDayController:
    
    def __init__(self, usecase: GetSessionsByDayUsecase):
        self.GetSessionsByDayUsecase = usecase
    
    def __call__(self, request: IRequest) -> IResponse:
        try:
            # Validate required parameters
            if request.data.get('day') is None:
                raise MissingParameters('day')
            
            day = request.data.get('day')
            
            # Call use case
            sessions = self.GetSessionsByDayUsecase(day=day)
            
            # Create view model and return
            viewmodel = GetSessionsByDayViewmodel(sessions=sessions, day=day)
            return OK(viewmodel.to_dict())
        
        except MissingParameters as err:
            return BadRequest(body=err.message)
        except EntityError as err:
            return BadRequest(body=err.message)
        except Exception as err:
            return InternalServerError(body=err.args[0])
