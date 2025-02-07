import uuid6

UUID = uuid6.UUID


def generate_uuid() -> UUID:
    return uuid6.uuid7()


def uuid_to_bin(u: UUID) -> bytes:
    return u.bytes


def bin_to_uuid(b: bytes) -> UUID:
    return UUID(bytes=b)


def uuid_to_str(u: UUID) -> str:
    return str(u)


def str_to_uuid(s: str) -> UUID:
    try:
        return UUID(s)
    except ValueError:
        raise ValueError(f"Invalid UUID string format: {s}")
