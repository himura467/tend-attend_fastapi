import os
from typing import TypedDict

from ta_core.constants.constants import (
    AURORA_COMMON_DBNAME,
    AURORA_SEQUENCE_DBNAME,
    AURORA_SHARD_DBNAME_PREFIX,
    AWS_RDS_CLUSTER_INSTANCE_PORT,
    AWS_RDS_CLUSTER_INSTANCE_URL,
    AWS_RDS_CLUSTER_MASTER_USERNAME,
    DB_SHARD_COUNT,
)
from ta_core.constants.secrets import AWS_RDS_CLUSTER_MASTER_PASSWORD


class DBConfig(TypedDict):
    host: str
    port: int
    user: str
    password: str
    common_dbname: str
    sequence_dbname: str
    shard_dbname_prefix: str
    unix_socket_path: str | None


_DEFAULT_DB_CONFIG: DBConfig = {
    "host": "127.0.0.1",
    "port": 13306,
    "user": "user",
    "password": "password",
    "common_dbname": "tend_attend_common",
    "sequence_dbname": "tend_attend_sequence",
    "shard_dbname_prefix": "tend_attend_shard",
    "unix_socket_path": None,
}

DB_CONFIG: DBConfig = {
    "host": AWS_RDS_CLUSTER_INSTANCE_URL or _DEFAULT_DB_CONFIG["host"],
    "port": AWS_RDS_CLUSTER_INSTANCE_PORT or _DEFAULT_DB_CONFIG["port"],
    "user": AWS_RDS_CLUSTER_MASTER_USERNAME or _DEFAULT_DB_CONFIG["user"],
    "password": AWS_RDS_CLUSTER_MASTER_PASSWORD or _DEFAULT_DB_CONFIG["password"],
    "common_dbname": AURORA_COMMON_DBNAME or _DEFAULT_DB_CONFIG["common_dbname"],
    "sequence_dbname": AURORA_SEQUENCE_DBNAME or _DEFAULT_DB_CONFIG["sequence_dbname"],
    "shard_dbname_prefix": AURORA_SHARD_DBNAME_PREFIX
    or _DEFAULT_DB_CONFIG["shard_dbname_prefix"],
    "unix_socket_path": os.environ.get(
        "DB_INSTANCE_UNIX_SOCKET", _DEFAULT_DB_CONFIG["unix_socket_path"]
    ),
}

_SHARD_DB_URLS: tuple[str, ...] = ()
if DB_CONFIG["unix_socket_path"] is not None:
    _COMMON_DB_URL = f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@/{DB_CONFIG['common_dbname']}?unix_socket={DB_CONFIG['unix_socket_path']}"
    _SEQUENCE_DB_URL = f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@/{DB_CONFIG['sequence_dbname']}?unix_socket={DB_CONFIG['unix_socket_path']}"
    _SHARD_DB_URLS = tuple(
        f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@/{DB_CONFIG['shard_dbname_prefix']}{i}?unix_socket={DB_CONFIG['unix_socket_path']}"
        for i in range(DB_SHARD_COUNT)
    )
else:
    _COMMON_DB_URL = f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['common_dbname']}"
    _SEQUENCE_DB_URL = f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['sequence_dbname']}"
    _SHARD_DB_URLS = tuple(
        f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['shard_dbname_prefix']}{i}"
        for i in range(DB_SHARD_COUNT)
    )

COMMON_DB_CONNECTION_KEY = "common"
SEQUENCE_DB_CONNECTION_KEY = "sequence"
SHARD_DB_CONNECTION_KEYS = tuple(f"shard{i}" for i in range(DB_SHARD_COUNT))
CONNECTIONS = {
    COMMON_DB_CONNECTION_KEY: _COMMON_DB_URL,
    SEQUENCE_DB_CONNECTION_KEY: _SEQUENCE_DB_URL,
    **{
        connection_key: url
        for connection_key, url in zip(SHARD_DB_CONNECTION_KEYS, _SHARD_DB_URLS)
    },
}
