import socket
import time
from writer import Writer
from beacon_codec import pack_beacon
from network_physics import attempt_transmission
from security_config import compute_hmac, MSG_TYPE_BEACON

HOST = "192.168.27.133"
PORT = 65432

def send_node(node):
    success, distance, loss_prob = attempt_transmission(node.x, node.y)
    print(f"[WRITER] Distance to ONA: {distance:.1f}m (loss probability: {loss_prob:.2f})")

    if not success:
        print(f"[WRITER] TRANSMISSION FAILED — out of range or lost in transit. "
              f"Beacon {node.node_id} NOT delivered.")
        return

    packed = pack_beacon(
        x=node.x, y=node.y, timestamp=node.timestamp,
        event=node.event, pod=node.pod
    )
    print(f"[WRITER] Beacon packed into {len(packed)} bytes: {packed.hex()}")

    type_byte = bytes([MSG_TYPE_BEACON])
    mac = compute_hmac(type_byte, packed)
    message = type_byte + packed + mac
    print(f"[WRITER] Authenticated message ready ({len(message)} bytes)")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        client_socket.sendall(message)
        response = client_socket.recv(1024)
        print(f"[WRITER] Server replied: {response}")


if __name__ == "__main__":
    writer = Writer("WRITER_1")
    writer.move_to(x=15, y=0, event="VICTIM", pod=0.9)

    if writer.dropped_nodes:
        send_node(writer.dropped_nodes[0])
    else:
        print("[WRITER] No node was dropped, nothing to send.")
