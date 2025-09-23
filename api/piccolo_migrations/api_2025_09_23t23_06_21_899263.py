from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import ForeignKey


ID = "2025-09-23T23:06:21:899263"
VERSION = "1.28.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="api", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="Prediction",
        tablename="prediction",
        column_name="club",
        db_column_name="club",
        params={"null": True},
        old_params={"null": False},
        column_class=ForeignKey,
        old_column_class=ForeignKey,
        schema=None,
    )

    return manager
