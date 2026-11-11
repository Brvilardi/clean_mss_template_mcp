from src.modules.sync_sessions.app.sync_sessions_viewmodel import SyncSessionsViewmodel


class Test_SyncSessionsViewmodel:
    def test_sync_sessions_viewmodel_with_inserts_and_updates(self):
        sync_result = {
            "inserted": 10,
            "updated": 5,
            "total": 15
        }
        
        viewmodel = SyncSessionsViewmodel(sync_result)
        response = viewmodel.to_dict()
        
        expected = {
            "message": "Sessions synced successfully",
            "inserted": 10,
            "updated": 5,
            "total": 15
        }
        
        assert response == expected

    def test_sync_sessions_viewmodel_only_inserts(self):
        sync_result = {
            "inserted": 20,
            "updated": 0,
            "total": 20
        }
        
        viewmodel = SyncSessionsViewmodel(sync_result)
        response = viewmodel.to_dict()
        
        expected = {
            "message": "Sessions synced successfully",
            "inserted": 20,
            "updated": 0,
            "total": 20
        }
        
        assert response == expected

    def test_sync_sessions_viewmodel_only_updates(self):
        sync_result = {
            "inserted": 0,
            "updated": 8,
            "total": 8
        }
        
        viewmodel = SyncSessionsViewmodel(sync_result)
        response = viewmodel.to_dict()
        
        expected = {
            "message": "Sessions synced successfully",
            "inserted": 0,
            "updated": 8,
            "total": 8
        }
        
        assert response == expected

    def test_sync_sessions_viewmodel_no_changes(self):
        sync_result = {
            "inserted": 0,
            "updated": 0,
            "total": 0
        }
        
        viewmodel = SyncSessionsViewmodel(sync_result)
        response = viewmodel.to_dict()
        
        expected = {
            "message": "Sessions synced successfully",
            "inserted": 0,
            "updated": 0,
            "total": 0
        }
        
        assert response == expected

    def test_sync_sessions_viewmodel_with_empty_dict(self):
        sync_result = {}
        
        viewmodel = SyncSessionsViewmodel(sync_result)
        response = viewmodel.to_dict()
        
        expected = {
            "message": "Sessions synced successfully",
            "inserted": 0,
            "updated": 0,
            "total": 0
        }
        
        assert response == expected
