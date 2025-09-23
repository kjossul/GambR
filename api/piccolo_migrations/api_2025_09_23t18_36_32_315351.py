from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
from piccolo.columns.column_types import Boolean
from piccolo.columns.column_types import ForeignKey
from piccolo.columns.column_types import Integer
from piccolo.columns.column_types import Serial
from piccolo.columns.column_types import Timestamp
from piccolo.columns.column_types import Varchar
from piccolo.columns.defaults.timestamp import TimestampNow
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table


class Player(Table, tablename="player", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name="id",
        secret=False,
    )


class Track(Table, tablename="track", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name="id",
        secret=False,
    )


ID = "2025-09-23T18:36:32:315351"
VERSION = "1.28.0"
DESCRIPTION = "Added record table"


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="api", description=DESCRIPTION
    )

    manager.add_table(
        class_name="TrackmaniaRecord",
        tablename="trackmania_record",
        schema=None,
        columns=None,
    )

    manager.add_column(
        table_class_name="TrackmaniaRecord",
        tablename="trackmania_record",
        column_name="player",
        db_column_name="player",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Player,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="TrackmaniaRecord",
        tablename="trackmania_record",
        column_name="track",
        db_column_name="track",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Track,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="TrackmaniaRecord",
        tablename="trackmania_record",
        column_name="time",
        db_column_name="time",
        column_class_name="Integer",
        column_class=Integer,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="TrackmaniaRecord",
        tablename="trackmania_record",
        column_name="nadeo_timestamp",
        db_column_name="nadeo_timestamp",
        column_class_name="Timestamp",
        column_class=Timestamp,
        params={
            "default": TimestampNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="TrackmaniaRecord",
        tablename="trackmania_record",
        column_name="created_at",
        db_column_name="created_at",
        column_class_name="Timestamp",
        column_class=Timestamp,
        params={
            "default": TimestampNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="TrackmaniaRecord",
        tablename="trackmania_record",
        column_name="checked_by",
        db_column_name="checked_by",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
            "default": "",
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Prediction",
        tablename="prediction",
        column_name="processed",
        db_column_name="processed",
        column_class_name="Boolean",
        column_class=Boolean,
        params={
            "default": False,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.rename_column(
        table_class_name="Prediction",
        tablename="prediction",
        old_column_name="close_time",
        new_column_name="closes_at",
        old_db_column_name="close_time",
        new_db_column_name="closes_at",
        schema=None,
    )

    manager.rename_column(
        table_class_name="Prediction",
        tablename="prediction",
        old_column_name="end_time",
        new_column_name="ends_at",
        old_db_column_name="end_time",
        new_db_column_name="ends_at",
        schema=None,
    )

    return manager
