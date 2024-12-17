import os
from typing import TypedDict

from ta_core.constants.constants import (
    AURORA_DATABASE_NAME,
    AWS_RDS_CLUSTER_INSTANCE_PORT,
    AWS_RDS_CLUSTER_INSTANCE_URL,
    AWS_RDS_CLUSTER_MASTER_USERNAME,
)
from ta_core.constants.secrets import AWS_RDS_CLUSTER_MASTER_PASSWORD


class DBConfig(TypedDict):
    host: str
    port: int
    user: str
    password: str
    common_dbname: str
    sequence_dbname: str
    shard_dbnames: tuple[str, ...]
    unix_socket_path: str | None


DB_SHARD_COUNT = 2

_DEFAULT_DB_CONFIG: DBConfig = {
    "host": "127.0.0.1",
    "port": 13306,
    "user": "user",
    "password": "password",
    "common_dbname": "tend_attend_common",
    "sequence_dbname": "tend_attend_sequence",
    "shard_dbnames": tuple(f"tend_attend_shard{i}" for i in range(0, DB_SHARD_COUNT)),
    "unix_socket_path": None,
}

DB_CONFIG: DBConfig = {
    "host": AWS_RDS_CLUSTER_INSTANCE_URL or _DEFAULT_DB_CONFIG["host"],
    "port": int(AWS_RDS_CLUSTER_INSTANCE_PORT or _DEFAULT_DB_CONFIG["port"]),
    "user": AWS_RDS_CLUSTER_MASTER_USERNAME or _DEFAULT_DB_CONFIG["user"],
    "password": AWS_RDS_CLUSTER_MASTER_PASSWORD or _DEFAULT_DB_CONFIG["password"],
    "common_dbname": AURORA_DATABASE_NAME or _DEFAULT_DB_CONFIG["common_dbname"],
    "sequence_dbname": AURORA_DATABASE_NAME or _DEFAULT_DB_CONFIG["sequence_dbname"],
    "shard_dbnames": tuple(
        AURORA_DATABASE_NAME or _DEFAULT_DB_CONFIG["shard_dbnames"][i]
        for i in range(0, DB_SHARD_COUNT)
    ),
    "unix_socket_path": os.environ.get(
        "DB_INSTANCE_UNIX_SOCKET", _DEFAULT_DB_CONFIG["unix_socket_path"]
    ),
}

DB_SHARD_CONNECTION_STRS: tuple[str, ...] = ()
if DB_CONFIG["unix_socket_path"] is not None:
    _DB_COMMON_CONNECTION_STR = f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@/{DB_CONFIG['common_dbname']}?unix_socket={DB_CONFIG['unix_socket_path']}"
    _DB_SEQUENCE_CONNECTION_STR = f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@/{DB_CONFIG['sequence_dbname']}?unix_socket={DB_CONFIG['unix_socket_path']}"
    for i in range(0, DB_SHARD_COUNT):
        DB_SHARD_CONNECTION_STRS += (
            f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@/{DB_CONFIG['shard_dbnames'][i]}?unix_socket={DB_CONFIG['unix_socket_path']}",
        )
else:
    _DB_COMMON_CONNECTION_STR = f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['common_dbname']}"
    _DB_SEQUENCE_CONNECTION_STR = f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['sequence_dbname']}"
    for i in range(0, DB_SHARD_COUNT):
        DB_SHARD_CONNECTION_STRS += (
            f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['shard_dbnames'][i]}",
        )

DB_COMMON_CONNECTION_KEY = "common"
DB_SEQUENCE_CONNECTION_KEY = "sequence"
DB_SHARD_CONNECTION_KEYS = tuple(f"shard{i}" for i in range(0, DB_SHARD_COUNT))
CONNECTIONS = {
    DB_COMMON_CONNECTION_KEY: _DB_COMMON_CONNECTION_STR,
    DB_SEQUENCE_CONNECTION_KEY: _DB_SEQUENCE_CONNECTION_STR,
    **{
        connection_key: connection_str
        for connection_key, connection_str in zip(
            DB_SHARD_CONNECTION_KEYS, DB_SHARD_CONNECTION_STRS
        )
    },
}
