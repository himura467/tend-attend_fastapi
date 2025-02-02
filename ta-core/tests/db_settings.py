from typing import TypedDict


class DBConfig(TypedDict):
    host: str
    port: int
    user: str
    password: str
    common_dbname: str
    sequence_dbname: str
    shard_dbname_prefix: str
    unix_socket_path: str | None


TEST_DB_SHARD_COUNT = 2

TEST_DB_CONFIG: DBConfig = {
    "host": "127.0.0.1",
    "port": 13306,
    "user": "user",
    "password": "password",
    "common_dbname": "test_ta_common",
    "sequence_dbname": "test_ta_sequence",
    "shard_dbname_prefix": "test_ta_shard",
    "unix_socket_path": None,
}

_TEST_SHARD_DB_URLS: tuple[str, ...] = ()
if TEST_DB_CONFIG["unix_socket_path"] is not None:
    _TEST_COMMON_DB_URL = f"mysql+aiomysql://{TEST_DB_CONFIG['user']}:{TEST_DB_CONFIG['password']}@/{TEST_DB_CONFIG['common_dbname']}?unix_socket={TEST_DB_CONFIG['unix_socket_path']}"
    _TEST_SEQUENCE_DB_URL = f"mysql+aiomysql://{TEST_DB_CONFIG['user']}:{TEST_DB_CONFIG['password']}@/{TEST_DB_CONFIG['sequence_dbname']}?unix_socket={TEST_DB_CONFIG['unix_socket_path']}"
    _TEST_SHARD_DB_URLS = tuple(
        f"mysql+aiomysql://{TEST_DB_CONFIG['user']}:{TEST_DB_CONFIG['password']}@/{TEST_DB_CONFIG['shard_dbname_prefix']}{i}?unix_socket={TEST_DB_CONFIG['unix_socket_path']}"
        for i in range(TEST_DB_SHARD_COUNT)
    )
else:
    _TEST_COMMON_DB_URL = f"mysql+aiomysql://{TEST_DB_CONFIG['user']}:{TEST_DB_CONFIG['password']}@{TEST_DB_CONFIG['host']}:{TEST_DB_CONFIG['port']}/{TEST_DB_CONFIG['common_dbname']}"
    _TEST_SEQUENCE_DB_URL = f"mysql+aiomysql://{TEST_DB_CONFIG['user']}:{TEST_DB_CONFIG['password']}@{TEST_DB_CONFIG['host']}:{TEST_DB_CONFIG['port']}/{TEST_DB_CONFIG['sequence_dbname']}"
    _TEST_SHARD_DB_URLS = tuple(
        f"mysql+aiomysql://{TEST_DB_CONFIG['user']}:{TEST_DB_CONFIG['password']}@{TEST_DB_CONFIG['host']}:{TEST_DB_CONFIG['port']}/{TEST_DB_CONFIG['shard_dbname_prefix']}{i}"
        for i in range(TEST_DB_SHARD_COUNT)
    )

TEST_COMMON_DB_CONNECTION_KEY = "common"
TEST_SEQUENCE_DB_CONNECTION_KEY = "sequence"
TEST_SHARD_DB_CONNECTION_KEYS = tuple(f"shard{i}" for i in range(TEST_DB_SHARD_COUNT))
TEST_CONNECTIONS = {
    TEST_COMMON_DB_CONNECTION_KEY: _TEST_COMMON_DB_URL,
    TEST_SEQUENCE_DB_CONNECTION_KEY: _TEST_SEQUENCE_DB_URL,
    **{
        connection_key: url
        for connection_key, url in zip(
            TEST_SHARD_DB_CONNECTION_KEYS, _TEST_SHARD_DB_URLS
        )
    },
}
