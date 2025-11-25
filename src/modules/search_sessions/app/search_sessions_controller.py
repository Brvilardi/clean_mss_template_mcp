from src.shared.helpers.external_interfaces.external_interface import IResponse, IRequest
from .search_sessions_usecase import SearchSessionsUsecase
from .search_sessions_viewmodel import SearchSessionsViewmodel
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.helpers.external_interfaces.http_codes import OK, BadRequest, InternalServerError


class SearchSessionsController:
    
    def __init__(self, usecase: SearchSessionsUsecase):
        self.SearchSessionsUsecase = usecase
    
    def __call__(self, request: IRequest) -> IResponse:
        try:
            # Extract query parameters from request
            day = request.data.get('day')
            venue = request.data.get('venue')
            level_str = request.data.get('level')
            keywords = request.data.get('keywords')
            speaker = request.data.get('speaker')
            session_type = request.data.get('session_type')
            page_size_str = request.data.get('page_size')
            next_page_token = request.data.get('next_page_token')
            
            # Convert level to int if provided
            level = None
            if level_str is not None:
                try:
                    level = int(level_str)
                except (ValueError, TypeError):
                    raise EntityError("level")
            
            # Convert page_size to int if provided, default to 50
            page_size = 50
            if page_size_str is not None:
                try:
                    page_size = int(page_size_str)
                except (ValueError, TypeError):
                    raise EntityError("page_size")
            
            # Call use case with extracted parameters
            sessions, next_token = self.SearchSessionsUsecase(
                day=day,
                venue=venue,
                level=level,
                keywords=keywords,
                speaker=speaker,
                session_type=session_type,
                page_size=page_size,
                last_evaluated_key=next_page_token
            )
            
            # Create view model and return
            viewmodel = SearchSessionsViewmodel(
                sessions=sessions,
                next_page_token=next_token,
                total_results=len(sessions)
            )
            return OK(viewmodel.to_dict())
        
        except EntityError as err:
            return BadRequest(body=err.message)
        except ValueError as err:
            return BadRequest(body=str(err))
        except Exception as err:
            return InternalServerError(body=err.args[0])
