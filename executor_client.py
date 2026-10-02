import socket
import json
from executor import Executor
from weak_node import WeakNode
from security_config import compute_hmac, MSG_TYPE_MISSION_REQUEST

HOST = "192.168.27.133"
PORT = 65432

def get_mission():
    type_byte = bytes([MSG_TYPE_MISSION_REQUEST])
    mac = compute_hmac(type_byte, b"")
    message = type_byte + mac

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        client_socket.sendall(message)

        chunks = []
        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
        response = b"".join(chunks)

        if response.startswith(b"ERROR"):
            print(f"[EXECUTOR] Server error: {response.decode('utf-8')}")
            return []

        beacons = json.loads(response.decode("utf-8"))
        print(f"[EXECUTOR] Received mission: {len(beacons)} beacon(s)")
        return beacons


if __name__ == "__main__":
    beacons_data = get_mission()
    nodes = [WeakNode.from_dict(b) for b in beacons_data]

    executor = Executor("EXECUTOR_1", read_range=5, speed=2.0)
    target = executor.pick_nearest_target(nodes)

    if target:
        executor.navigate_to(target.x, target.y)
        executor.scan_for_nodes(nodes)
    else:
        print(f"[{executor.executor_id}] No beacons available to navigate to.")