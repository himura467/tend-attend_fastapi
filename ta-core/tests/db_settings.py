import os
from typing import TypedDict


class DBConfig(TypedDict):
    host: str
    port: int
    user: str
    password: str
    db: str
    unix_socket_path: str | None


TEST_DB_SHARD_COUNT = 2

_DEFAULT_TEST_DB_CONFIG: DBConfig = {
    "host": "127.0.0.1",
    "port": 13306,
    "user": "user",
    "password": "password",
    "db": "tend_attend_common",
    "unix_socket_path": None,
}

TEST_DB_CONFIG: DBConfig = {
    "host": os.environ.get("TEST_DB_HOST", _DEFAULT_TEST_DB_CONFIG["host"]),
    "port": int(os.environ.get("TEST_DB_PORT", _DEFAULT_TEST_DB_CONFIG["port"])),
    "user": os.environ.get("TEST_DB_USER", _DEFAULT_TEST_DB_CONFIG["user"]),
    "password": os.environ.get("TEST_DB_PASSWORD", _DEFAULT_TEST_DB_CONFIG["password"]),
    "db": os.environ.get("TEST_DB_DB", _DEFAULT_TEST_DB_CONFIG["db"]),
    "unix_socket_path": os.environ.get(
        "TEST_DB_INSTANCE_UNIX_SOCKET", _DEFAULT_TEST_DB_CONFIG["unix_socket_path"]
    ),
}

prefix = "tend_attend"
shard_ids = tuple(range(0, TEST_DB_SHARD_COUNT))

TEST_DB_SHARD_CONNECTION_STRS: tuple[str, ...] = ()
if TEST_DB_CONFIG["unix_socket_path"] is not None:
    _TEST_DB_COMMON_CONNECTION_STR = f"mysql+aiomysql://{TEST_DB_CONFIG['user']}:{TEST_DB_CONFIG['password']}@/{TEST_DB_CONFIG['db']}?unix_socket={TEST_DB_CONFIG['unix_socket_path']}"
    _TEST_DB_SEQUENCE_CONNECTION_STR = f"mysql+aiomysql://{TEST_DB_CONFIG['user']}:{TEST_DB_CONFIG['password']}@/{prefix}_sequence?unix_socket={TEST_DB_CONFIG['unix_socket_path']}"
    for shard_id in shard_ids:
        TEST_DB_SHARD_CONNECTION_STRS += (
            f"mysql+aiomysql://{TEST_DB_CONFIG['user']}:{TEST_DB_CONFIG['password']}@/{prefix}_shard{shard_id}?unix_socket={TEST_DB_CONFIG['unix_socket_path']}",
        )
else:
    _TEST_DB_COMMON_CONNECTION_STR = f"mysql+aiomysql://{TEST_DB_CONFIG['user']}:{TEST_DB_CONFIG['password']}@{TEST_DB_CONFIG['host']}:{TEST_DB_CONFIG['port']}/{TEST_DB_CONFIG['db']}"
    _TEST_DB_SEQUENCE_CONNECTION_STR = f"mysql+aiomysql://{TEST_DB_CONFIG['user']}:{TEST_DB_CONFIG['password']}@{TEST_DB_CONFIG['host']}:{TEST_DB_CONFIG['port']}/{prefix}_sequence"
    for shard_id in shard_ids:
        TEST_DB_SHARD_CONNECTION_STRS += (
            f"mysql+aiomysql://{TEST_DB_CONFIG['user']}:{TEST_DB_CONFIG['password']}@{TEST_DB_CONFIG['host']}:{TEST_DB_CONFIG['port']}/{prefix}_shard{shard_id}",
        )

TEST_DB_COMMON_CONNECTION_KEY = "common"
TEST_DB_SEQUENCE_CONNECTION_KEY = "sequence"
TEST_DB_SHARD_CONNECTION_KEYS = tuple(f"shard{shard_id}" for shard_id in shard_ids)
CONNECTIONS = {
    TEST_DB_COMMON_CONNECTION_KEY: _TEST_DB_COMMON_CONNECTION_STR,
    TEST_DB_SEQUENCE_CONNECTION_KEY: _TEST_DB_SEQUENCE_CONNECTION_STR,
    **{
        connection_key: connection_str
        for connection_key, connection_str in zip(
            TEST_DB_SHARD_CONNECTION_KEYS, TEST_DB_SHARD_CONNECTION_STRS
        )
    },
}
