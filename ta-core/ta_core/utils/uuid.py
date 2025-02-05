import uuid

import uuid6


def generate_uuid() -> uuid.UUID:
    return uuid6.uuid7()


def uuid_to_bin(u: uuid.UUID) -> bytes:
    return u.bytes


def bin_to_uuid(b: bytes) -> uuid.UUID:
    return uuid.UUID(bytes=b)
