from unittest.mock import Mock
from src.modules.sync_sessions.app.sync_sessions_controller import SyncSessionsController
from src.modules.sync_sessions.app.sync_sessions_usecase import SyncSessionsUsecase
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_SyncSessionsController:

    def test_sync_sessions_controller_success(self):
        """Test successful sync operation returns 200 with statistics"""
        repo_mock = SessionRepositoryMock()
        sync_sessions_usecase = SyncSessionsUsecase(repo_mock)
        controller = SyncSessionsController(sync_sessions_usecase)

        response = controller(None)

        assert response.status_code == 200
        assert "message" in response.body
        assert response.body["message"] == "Sessions synced successfully"
        assert "inserted" in response.body
        assert "updated" in response.body
        assert "total" in response.body
        assert isinstance(response.body["inserted"], int)
        assert isinstance(response.body["updated"], int)
        assert isinstance(response.body["total"], int)

    def test_sync_sessions_controller_connection_error(self):
        """Test connection error returns 503 Service Unavailable"""
        # Create a mock repository that raises ConnectionError
        repo_mock = Mock()
        repo_mock.sync_sessions_from_api.side_effect = ConnectionError("External API unreachable")
        
        sync_sessions_usecase = SyncSessionsUsecase(repo_mock)
        controller = SyncSessionsController(sync_sessions_usecase)

        response = controller(None)

        assert response.status_code == 503
        assert "External API unreachable" in response.body

    def test_sync_sessions_controller_unexpected_error(self):
        """Test unexpected error returns 500 Internal Server Error"""
        # Create a mock repository that raises a generic exception
        repo_mock = Mock()
        repo_mock.sync_sessions_from_api.side_effect = Exception("Unexpected database error")
        
        sync_sessions_usecase = SyncSessionsUsecase(repo_mock)
        controller = SyncSessionsController(sync_sessions_usecase)

        response = controller(None)

        assert response.status_code == 500
        assert "Unexpected database error" in response.body
