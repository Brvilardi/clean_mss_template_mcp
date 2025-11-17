from src.shared.helpers.external_interfaces.external_interface import IResponse, IRequest
from .get_sessions_by_level_usecase import GetSessionsByLevelUsecase
from .get_sessions_by_level_viewmodel import GetSessionsByLevelViewmodel
from src.shared.helpers.errors.controller_errors import MissingParameters, WrongTypeParameter
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.helpers.external_interfaces.http_codes import OK, BadRequest, InternalServerError


class GetSessionsByLevelController:
    
    def __init__(self, usecase: GetSessionsByLevelUsecase):
        self.GetSessionsByLevelUsecase = usecase
    
    def __call__(self, request: IRequest) -> IResponse:
        try:
            # Validate required parameters
            if request.data.get('level_values') is None:
                raise MissingParameters('level_values')
            
            # Parse comma-separated level_values string
            level_values_str = request.data.get('level_values')
            try:
                # Split by comma and convert to integers
                level_values = [int(val.strip()) for val in level_values_str.split(',')]
            except (ValueError, TypeError, AttributeError):
                raise WrongTypeParameter(
                    fieldName='level_values',
                    fieldTypeExpected='comma-separated integers (e.g., "100,200")',
                    fieldTypeReceived=type(level_values_str).__name__
                )
            
            # Call use case
            sessions = self.GetSessionsByLevelUsecase(level_values=level_values)
            
            # Create view model and return
            viewmodel = GetSessionsByLevelViewmodel(sessions=sessions, level_values=level_values)
            return OK(viewmodel.to_dict())
        
        except MissingParameters as err:
            return BadRequest(body=err.message)
        except WrongTypeParameter as err:
            return BadRequest(body=err.message)
        except EntityError as err:
            return BadRequest(body=err.message)
        except Exception as err:
            return InternalServerError(body=err.args[0])
