from src.modules.get_all_sessions.app.get_all_sessions_usecase import GetAllSessionsUsecase
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetAllSessionsUsecase:

    def test_get_all_sessions(self):
        """Test retrieving all sessions from repository with data."""
        repo = SessionRepositoryMock()
        usecase = GetAllSessionsUsecase(repo)

        sessions = usecase()

        assert len(sessions) == 5
        assert sessions[0].short_id == "TNC301"
        assert sessions[0].title == "Accelerate VMware Migration with AWS Transform"
        assert sessions[1].short_id == "SVS201"
        assert sessions[2].short_id == "SEC101"
        assert sessions[3].short_id == "DAT401"
        assert sessions[4].short_id == "CON202"

    def test_get_all_sessions_empty_repository(self):
        """Test retrieving sessions from empty repository."""
        repo = SessionRepositoryMock()
        # Clear the pre-populated data
        repo.sessions = []
        usecase = GetAllSessionsUsecase(repo)

        sessions = usecase()

        assert len(sessions) == 0
        assert sessions == []
