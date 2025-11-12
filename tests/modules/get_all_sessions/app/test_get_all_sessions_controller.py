from src.modules.get_all_sessions.app.get_all_sessions_controller import GetAllSessionsController
from src.modules.get_all_sessions.app.get_all_sessions_usecase import GetAllSessionsUsecase
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetAllSessionsController:

    def test_get_all_sessions_controller(self):
        repo_mock = SessionRepositoryMock()
        get_all_sessions_usecase = GetAllSessionsUsecase(repo_mock)
        controller = GetAllSessionsController(get_all_sessions_usecase)

        response = controller(None)

        assert response.status_code == 200

    def test_get_all_sessions_controller_with_empty_repository(self):
        repo_mock = SessionRepositoryMock()
        # Clear the mock repository
        repo_mock.sessions = []
        get_all_sessions_usecase = GetAllSessionsUsecase(repo_mock)
        controller = GetAllSessionsController(get_all_sessions_usecase)

        response = controller(None)

        assert response.status_code == 200
        assert response.body['sessions'] == []
        assert response.body['count'] == 0
