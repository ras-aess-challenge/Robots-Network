import socket
import json

HOST = "0.0.0.0"
PORT = 65432

COMMAND_POST_HOST = "127.0.0.1"
COMMAND_POST_PORT = 65433

def forward_to_command_post(message_bytes):
    """Sends raw bytes to the Command Post and returns its raw response."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cp_socket:
            cp_socket.connect((COMMAND_POST_HOST, COMMAND_POST_PORT))
            cp_socket.sendall(message_bytes)
            return cp_socket.recv(4096)
    except ConnectionRefusedError:
        print("[STRONG_NODE] WARNING: Could not reach Command Post — is it running?")
        return b"ERROR: command post unreachable"

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[STRONG_NODE] Listening on {HOST}:{PORT}...")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"[STRONG_NODE] Connected by {addr}")
                data = conn.recv(4096)
                if not data:
                    continue

                message = data.decode("utf-8")

                if message == "GET_MISSION":
                    print(f"[STRONG_NODE] Relaying mission request from {addr} to Command Post")
                    cp_response = forward_to_command_post(data)
                    conn.sendall(cp_response)
                    print(f"[STRONG_NODE] Relayed Command Post response back to {addr}")
                    continue

                try:
                    payload = json.loads(message)
                    print(f"[STRONG_NODE] Parsed beacon: "
                          f"node_id={payload['node_id']}, "
                          f"x={payload['x']:.1f}, y={payload['y']:.1f}, "
                          f"event={payload['event']}, pod={payload['pod']}")
                    conn.sendall(f"RECEIVED {payload['node_id']}".encode("utf-8"))
                    forward_to_command_post(data)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"[STRONG_NODE] Invalid payload rejected: {e}")
                    conn.sendall(b"ERROR: invalid payload")


if __name__ == "__main__":
    start_server()