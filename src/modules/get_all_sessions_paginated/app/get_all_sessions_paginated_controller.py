from src.shared.helpers.external_interfaces.external_interface import IResponse, IRequest
from .get_all_sessions_paginated_usecase import GetAllSessionsPaginatedUsecase
from .get_all_sessions_paginated_viewmodel import GetAllSessionsPaginatedViewmodel
from src.shared.helpers.errors.controller_errors import MissingParameters, WrongTypeParameter
from src.shared.helpers.external_interfaces.http_codes import OK, BadRequest, InternalServerError


class GetAllSessionsPaginatedController:
    """
    Controller for handling paginated get all sessions requests.
    """
    
    def __init__(self, usecase: GetAllSessionsPaginatedUsecase):
        self.usecase = usecase
    
    def __call__(self, request: IRequest) -> IResponse:
        try:
            # Extract page_size from query parameters (required)
            page_size = request.data.get('page_size')
            if page_size is None:
                raise MissingParameters('page_size')
            
            # Convert page_size to int
            try:
                page_size = int(page_size)
            except (ValueError, TypeError):
                raise WrongTypeParameter(
                    'page_size',
                    'int',
                    type(page_size).__name__
                )
            
            # Extract last_evaluated_key from query parameters (optional)
            last_evaluated_key = request.data.get('last_evaluated_key')
            
            # Call use case with pagination parameters
            sessions, next_token = self.usecase(
                page_size=page_size,
                last_evaluated_key=last_evaluated_key
            )
            
            # Create view model with results
            viewmodel = GetAllSessionsPaginatedViewmodel(
                sessions=sessions,
                page_size=page_size,
                next_token=next_token
            )
            
            return OK(viewmodel.to_dict())
        
        except ValueError as err:
            # Pagination validation errors (including token expiration)
            return BadRequest(body=str(err))
        except MissingParameters as err:
            return BadRequest(body=err.message)
        except WrongTypeParameter as err:
            return BadRequest(body=err.message)
        except Exception as err:
            return InternalServerError(body=str(err))
