class SyncSessionsViewmodel:
    def __init__(self, sync_result: dict):
        self.inserted = sync_result.get("inserted", 0)
        self.updated = sync_result.get("updated", 0)
        self.total = sync_result.get("total", 0)

    def to_dict(self):
        return {
            "message": "Sessions synced successfully",
            "inserted": self.inserted,
            "updated": self.updated,
            "total": self.total
        }
