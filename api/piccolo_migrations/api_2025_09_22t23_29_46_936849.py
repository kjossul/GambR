from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
from piccolo.columns.column_types import Boolean
from piccolo.columns.column_types import ForeignKey
from piccolo.columns.column_types import Integer
from piccolo.columns.column_types import Interval
from piccolo.columns.column_types import Serial
from piccolo.columns.column_types import SmallInt
from piccolo.columns.column_types import Timestamp
from piccolo.columns.column_types import UUID
from piccolo.columns.column_types import Varchar
from piccolo.columns.defaults.interval import IntervalCustom
from piccolo.columns.defaults.timestamp import TimestampNow
from piccolo.columns.defaults.uuid import UUID4
from piccolo.columns.indexes import IndexMethod
from piccolo.constraint import UniqueConstraint
from piccolo.table import Table


class Club(Table, tablename="club", schema=None):
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


class Prediction(Table, tablename="prediction", schema=None):
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


ID = "2025-09-22T23:29:46:936849"
VERSION = "1.28.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="api", description=DESCRIPTION
    )

    manager.add_table(
        class_name="PlayerToPrediction",
        tablename="player_to_prediction",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="Prediction", tablename="prediction", schema=None, columns=None
    )

    manager.add_table(
        class_name="Player", tablename="player", schema=None, columns=None
    )

    manager.add_table(
        class_name="Club", tablename="club", schema=None, columns=None
    )

    manager.add_table(
        class_name="PlayerToClub",
        tablename="player_to_club",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="Track", tablename="track", schema=None, columns=None
    )

    manager.add_table(
        class_name="TrackToClub",
        tablename="track_to_club",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="Bet", tablename="bet", schema=None, columns=None
    )

    manager.add_column(
        table_class_name="PlayerToPrediction",
        tablename="player_to_prediction",
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
        table_class_name="PlayerToPrediction",
        tablename="player_to_prediction",
        column_name="prediction",
        db_column_name="prediction",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Prediction,
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
        table_class_name="PlayerToPrediction",
        tablename="player_to_prediction",
        column_name="result",
        db_column_name="result",
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
        table_class_name="Prediction",
        tablename="prediction",
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
        table_class_name="Prediction",
        tablename="prediction",
        column_name="club",
        db_column_name="club",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Club,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
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
        table_class_name="Prediction",
        tablename="prediction",
        column_name="type",
        db_column_name="type",
        column_class_name="SmallInt",
        column_class=SmallInt,
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
        table_class_name="Prediction",
        tablename="prediction",
        column_name="close_time",
        db_column_name="close_time",
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
        table_class_name="Prediction",
        tablename="prediction",
        column_name="end_time",
        db_column_name="end_time",
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
        table_class_name="Player",
        tablename="player",
        column_name="uuid",
        db_column_name="uuid",
        column_class_name="UUID",
        column_class=UUID,
        params={
            "default": UUID4(),
            "null": False,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Player",
        tablename="player",
        column_name="name",
        db_column_name="name",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
            "default": "",
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
        table_class_name="Player",
        tablename="player",
        column_name="secret",
        db_column_name="secret",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 64,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Club",
        tablename="club",
        column_name="name",
        db_column_name="name",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Club",
        tablename="club",
        column_name="points_name",
        db_column_name="points_name",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
            "default": "points",
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
        table_class_name="Club",
        tablename="club",
        column_name="restricted",
        db_column_name="restricted",
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

    manager.add_column(
        table_class_name="Club",
        tablename="club",
        column_name="visibility",
        db_column_name="visibility",
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

    manager.add_column(
        table_class_name="Club",
        tablename="club",
        column_name="automated_amount",
        db_column_name="automated_amount",
        column_class_name="SmallInt",
        column_class=SmallInt,
        params={
            "default": 2,
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
        table_class_name="Club",
        tablename="club",
        column_name="automated_frequency",
        db_column_name="automated_frequency",
        column_class_name="Interval",
        column_class=Interval,
        params={
            "default": IntervalCustom(
                weeks=0,
                days=0,
                hours=0,
                minutes=0,
                seconds=1800,
                milliseconds=0,
                microseconds=0,
            ),
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
        table_class_name="Club",
        tablename="club",
        column_name="automated_open",
        db_column_name="automated_open",
        column_class_name="Interval",
        column_class=Interval,
        params={
            "default": IntervalCustom(
                weeks=0,
                days=0,
                hours=0,
                minutes=0,
                seconds=300,
                milliseconds=0,
                microseconds=0,
            ),
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
        table_class_name="Club",
        tablename="club",
        column_name="automated_end",
        db_column_name="automated_end",
        column_class_name="Interval",
        column_class=Interval,
        params={
            "default": IntervalCustom(
                weeks=0,
                days=0,
                hours=0,
                minutes=0,
                seconds=21600,
                milliseconds=0,
                microseconds=0,
            ),
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
        table_class_name="PlayerToClub",
        tablename="player_to_club",
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
        table_class_name="PlayerToClub",
        tablename="player_to_club",
        column_name="club",
        db_column_name="club",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Club,
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
        table_class_name="PlayerToClub",
        tablename="player_to_club",
        column_name="points",
        db_column_name="points",
        column_class_name="Integer",
        column_class=Integer,
        params={
            "default": 1000,
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
        table_class_name="PlayerToClub",
        tablename="player_to_club",
        column_name="admin",
        db_column_name="admin",
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

    manager.add_column(
        table_class_name="Track",
        tablename="track",
        column_name="uuid",
        db_column_name="uuid",
        column_class_name="UUID",
        column_class=UUID,
        params={
            "default": UUID4(),
            "null": False,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Track",
        tablename="track",
        column_name="name",
        db_column_name="name",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
            "default": "",
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
        table_class_name="TrackToClub",
        tablename="track_to_club",
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
        table_class_name="TrackToClub",
        tablename="track_to_club",
        column_name="club",
        db_column_name="club",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Club,
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
        table_class_name="TrackToClub",
        tablename="track_to_club",
        column_name="counter",
        db_column_name="counter",
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
        table_class_name="Bet",
        tablename="bet",
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
        table_class_name="Bet",
        tablename="bet",
        column_name="prediction",
        db_column_name="prediction",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Prediction,
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
        table_class_name="Bet",
        tablename="bet",
        column_name="outcome",
        db_column_name="outcome",
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
        table_class_name="Bet",
        tablename="bet",
        column_name="points",
        db_column_name="points",
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

    manager.add_constraint(
        table_class_name="PlayerToPrediction",
        tablename="player_to_prediction",
        constraint_name="player_prediction_constraint",
        constraint_class=UniqueConstraint,
        params={"unique_columns": ["player", "prediction"]},
        schema=None,
    )

    manager.add_constraint(
        table_class_name="PlayerToClub",
        tablename="player_to_club",
        constraint_name="player_club_constraint",
        constraint_class=UniqueConstraint,
        params={"unique_columns": ["player", "club"]},
        schema=None,
    )

    manager.add_constraint(
        table_class_name="TrackToClub",
        tablename="track_to_club",
        constraint_name="track_club_constraint",
        constraint_class=UniqueConstraint,
        params={"unique_columns": ["track", "club"]},
        schema=None,
    )

    manager.add_constraint(
        table_class_name="Bet",
        tablename="bet",
        constraint_name="bet_constraint",
        constraint_class=UniqueConstraint,
        params={"unique_columns": ["player", "prediction"]},
        schema=None,
    )

    return manager
