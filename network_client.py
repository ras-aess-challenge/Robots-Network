"""Authenticated TCP transport shared by the writer and executor clients."""
import os
import socket

from security_config import compute_hmac

HOST = os.environ.get("NETWORK_HOST", "127.0.0.1")
PORT = int(os.environ.get("NETWORK_PORT", "65432"))
SOCKET_TIMEOUT = float(os.environ.get("SOCKET_TIMEOUT", "5"))
if SOCKET_TIMEOUT <= 0:
    raise ValueError("SOCKET_TIMEOUT must be positive")


def request(message_type, payload=b""):
    type_byte = bytes([message_type])
    message = type_byte + payload + compute_hmac(type_byte, payload)
    with socket.create_connection((HOST, PORT), timeout=SOCKET_TIMEOUT) as conn:
        conn.sendall(message)
        chunks = []
        while chunk := conn.recv(4096):
            chunks.append(chunk)
    response = b"".join(chunks)
    if not response:
        raise RuntimeError("Network returned an empty response")
    if response.startswith(b"ERROR"):
        raise RuntimeError(response.decode("utf-8"))
    return response
