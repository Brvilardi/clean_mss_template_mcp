from src.shared.helpers.external_interfaces.external_interface import IRequest
from .sync_sessions_usecase import SyncSessionsUsecase
from .sync_sessions_viewmodel import SyncSessionsViewmodel
from src.shared.helpers.errors.controller_errors import MissingParameters, WrongTypeParameter
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.helpers.errors.usecase_errors import NoItemsFound
from src.shared.helpers.external_interfaces.http_codes import NotFound, OK, BadRequest, InternalServerError, ServiceUnavailable


class SyncSessionsController:
    """
    Controller for syncing session data from external API.
    
    Handles HTTP requests to trigger synchronization of session data
    from the re:invent catalog API to the local database.
    """

    def __init__(self, usecase: SyncSessionsUsecase):
        """
        Initialize the controller with a sync sessions use case.
        
        Args:
            usecase: SyncSessionsUsecase instance
        """
        self.usecase = usecase

    def __call__(self, request: IRequest):
        """
        Handle sync sessions request.
        
        Args:
            request: HTTP request object (no parameters required)
            
        Returns:
            HTTP response with sync statistics or error
        """
        try:
            # Call use case to perform sync
            sync_result = self.usecase()

            # Create view model with results
            viewmodel = SyncSessionsViewmodel(sync_result)

            # Return 200 OK with sync statistics
            return OK(viewmodel.to_dict())

        except ConnectionError as err:
            # External API unreachable - return 503 Service Unavailable
            return ServiceUnavailable(body=str(err))

        except NoItemsFound as err:
            # Resource not found - return 404
            return NotFound(body=err.message)

        except MissingParameters as err:
            # Missing required parameters - return 400
            return BadRequest(body=err.message)

        except WrongTypeParameter as err:
            # Invalid parameter type - return 400
            return BadRequest(body=err.message)

        except EntityError as err:
            # Entity validation error - return 400
            return BadRequest(body=err.message)

        except Exception as err:
            # Unexpected error - return 500
            return InternalServerError(body=err.args[0])
