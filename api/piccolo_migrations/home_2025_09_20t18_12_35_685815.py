from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Integer


ID = "2025-09-20T18:12:35:685815"
VERSION = "1.22.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="home", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="PlayerToGroup",
        tablename="player_to_group",
        column_name="points",
        db_column_name="points",
        params={"default": 1000},
        old_params={"default": 0},
        column_class=Integer,
        old_column_class=Integer,
        schema=None,
    )

    return manager
