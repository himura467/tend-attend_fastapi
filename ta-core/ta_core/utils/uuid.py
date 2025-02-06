import uuid

import uuid6

UUID = uuid.UUID


def generate_uuid() -> UUID:
    return uuid6.uuid7()


def uuid_to_bin(u: UUID) -> bytes:
    return u.bytes


def bin_to_uuid(b: bytes) -> UUID:
    return UUID(bytes=b)
