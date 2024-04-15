import os
from typing import TypedDict


class DBConfig(TypedDict):
    host: str
    port: int
    user: str
    password: str
    db: str
    unix_socket_path: str | None


DB_SHARD_COUNT = 2

_DEFAULT_DB_CONFIG: DBConfig = {
    "host": "127.0.0.1",
    "port": 13306,
    "user": "user",
    "password": "password",
    "db": "tend_attend_common",
    "unix_socket_path": None,
}

DB_CONFIG: DBConfig = {
    "host": os.environ.get("DB_HOST", _DEFAULT_DB_CONFIG["host"]),
    "port": int(os.environ.get("DB_PORT", _DEFAULT_DB_CONFIG["port"])),
    "user": os.environ.get("DB_USER", _DEFAULT_DB_CONFIG["user"]),
    "password": os.environ.get("DB_PASSWORD", _DEFAULT_DB_CONFIG["password"]),
    "db": os.environ.get("DB_DB", _DEFAULT_DB_CONFIG["db"]),
    "unix_socket_path": os.environ.get(
        "DB_INSTANCE_UNIX_SOCKET", _DEFAULT_DB_CONFIG["unix_socket_path"]
    ),
}

prefix = "tend_attend"
shard_ids = tuple(range(0, DB_SHARD_COUNT))

DB_SHARD_CONNECTION_STRS: tuple[str, ...] = ()
if DB_CONFIG["unix_socket_path"] is not None:
    _DB_COMMON_CONNECTION_STR = f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@/{DB_CONFIG['db']}?unix_socket={DB_CONFIG['unix_socket_path']}"
    _DB_SEQUENCE_CONNECTION_STR = f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@/{prefix}_sequence?unix_socket={DB_CONFIG['unix_socket_path']}"
    for shard_id in shard_ids:
        DB_SHARD_CONNECTION_STRS += (
            f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@/{prefix}_shard{shard_id}?unix_socket={DB_CONFIG['unix_socket_path']}",
        )
else:
    _DB_COMMON_CONNECTION_STR = f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['db']}"
    _DB_SEQUENCE_CONNECTION_STR = f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{prefix}_sequence"
    for shard_id in shard_ids:
        DB_SHARD_CONNECTION_STRS += (
            f"mysql+aiomysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{prefix}_shard{shard_id}",
        )

DB_COMMON_CONNECTION_KEY = "common"
DB_SEQUENCE_CONNECTION_KEY = "sequence"
DB_SHARD_CONNECTION_KEYS = tuple(f"shard{shard_id}" for shard_id in shard_ids)
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
