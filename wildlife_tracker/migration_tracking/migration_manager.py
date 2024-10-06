from typing import Optional

from wildlife_tracker.migration_tracking.migration import Migration

from wildlife_tracker.migration_tracking.migration_path import MigrationPath
class MigrationManager:

    def cancel_migration(migration_id: int) -> None:
        pass
    def get_migration_by_id(migration_id: int) -> Migration:
        pass
    def get_migration_path_by_id(path_id: int) -> MigrationPath:
        pass
    