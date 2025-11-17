from src.shared.helpers.external_interfaces.external_interface import IResponse, IRequest
from .get_sessions_by_venue_usecase import GetSessionsByVenueUsecase
from .get_sessions_by_venue_viewmodel import GetSessionsByVenueViewmodel
from src.shared.helpers.errors.controller_errors import MissingParameters
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.helpers.external_interfaces.http_codes import OK, BadRequest, InternalServerError


class GetSessionsByVenueController:
    
    def __init__(self, usecase: GetSessionsByVenueUsecase):
        self.GetSessionsByVenueUsecase = usecase
    
    def __call__(self, request: IRequest) -> IResponse:
        try:
            # Extract venue_name from query parameters
            venue_name = request.data.get('venue_name')
            
            if venue_name is None:
                raise MissingParameters('venue_name')
            
            # Call use case
            sessions = self.GetSessionsByVenueUsecase(venue_name=venue_name)
            
            # Create view model and return
            viewmodel = GetSessionsByVenueViewmodel(sessions=sessions, venue_name=venue_name)
            return OK(viewmodel.to_dict())
        
        except MissingParameters as err:
            return BadRequest(body=err.message)
        except EntityError as err:
            return BadRequest(body=err.message)
        except Exception as err:
            return InternalServerError(body=err.args[0])
