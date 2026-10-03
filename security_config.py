import os
import hmac
import hashlib

SHARED_SECRET = os.environ.get("SHARED_SECRET", "").encode("utf-8")
if len(SHARED_SECRET) < 32:
    raise ValueError("SHARED_SECRET must contain at least 32 UTF-8 bytes")

MSG_TYPE_BEACON = 0x01
MSG_TYPE_MISSION_REQUEST = 0x02

HMAC_SIZE = 32  # SHA-256 digest size


def compute_hmac(type_byte: bytes, payload: bytes) -> bytes:
    return hmac.new(SHARED_SECRET, type_byte + payload, hashlib.sha256).digest()


def verify_hmac(type_byte: bytes, payload: bytes, received_hmac: bytes) -> bool:
    expected = compute_hmac(type_byte, payload)
    return hmac.compare_digest(expected, received_hmac)
