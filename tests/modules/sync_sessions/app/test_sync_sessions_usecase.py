from src.modules.sync_sessions.app.sync_sessions_usecase import SyncSessionsUsecase
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_SyncSessionsUsecase:

    def test_sync_sessions(self):
        """Test syncing sessions from external API with mock repository."""
        repo = SessionRepositoryMock()
        usecase = SyncSessionsUsecase(repo)

        # Get initial count
        initial_count = len(repo.get_all_sessions())

        # Execute sync
        result = usecase()

        # Verify return value structure
        assert "inserted" in result
        assert "updated" in result
        assert "total" in result
        
        # Verify counts
        assert isinstance(result["inserted"], int)
        assert isinstance(result["updated"], int)
        assert isinstance(result["total"], int)
        
        # Verify total calculation
        assert result["total"] == result["inserted"] + result["updated"]
        
        # Mock repository adds 1 new session on first sync
        assert result["inserted"] == 1
        assert result["updated"] == 0
        assert result["total"] == 1
        
        # Verify session was actually added
        final_count = len(repo.get_all_sessions())
        assert final_count == initial_count + 1

    def test_sync_sessions_return_structure(self):
        """Test that sync returns correct dictionary structure."""
        repo = SessionRepositoryMock()
        usecase = SyncSessionsUsecase(repo)

        result = usecase()

        # Verify all required keys are present
        assert set(result.keys()) == {"inserted", "updated", "total"}
        
        # Verify all values are integers
        for key, value in result.items():
            assert isinstance(value, int), f"{key} should be an integer"
            assert value >= 0, f"{key} should be non-negative"

    def test_sync_sessions_idempotent(self):
        """Test that syncing twice doesn't duplicate sessions."""
        repo = SessionRepositoryMock()
        usecase = SyncSessionsUsecase(repo)

        # First sync
        result1 = usecase()
        assert result1["inserted"] == 1
        
        # Second sync - should not insert duplicate
        result2 = usecase()
        assert result2["inserted"] == 0
        assert result2["updated"] == 0
        assert result2["total"] == 0
