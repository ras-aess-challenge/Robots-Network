from writer import Writer
from beacon_codec import pack_beacon
from network_physics import attempt_transmission
from network_client import request
from security_config import MSG_TYPE_BEACON


def send_node(node):
    success, distance, loss_prob = attempt_transmission(node.x, node.y)
    print(f"[WRITER] Distance to ONA: {distance:.1f}m (loss probability: {loss_prob:.2f})")
    if not success:
        raise RuntimeError(f"Beacon {node.node_id} lost or out of range; not delivered")

    packed = pack_beacon(
        x=node.x, y=node.y, timestamp=node.timestamp,
        event=node.event, pod=node.pod,
    )
    response = request(MSG_TYPE_BEACON, packed)
    expected = f"RECEIVED WN-{int(node.timestamp)}".encode()
    if response != expected:
        raise RuntimeError(f"Unexpected storage acknowledgement: {response!r}")
    print(f"[WRITER] Server replied: {response.decode()}")
    return response.decode().split(" ", 1)[1]


def run_writer():
    writer = Writer("WRITER_1")
    writer.move_to(x=15, y=0, event="VICTIM", pod=0.9)
    if not writer.dropped_nodes:
        raise RuntimeError("No beacon was dropped")
    # Preserve the existing demonstration, which produces one beacon at (10.5, 0).
    node_id = send_node(writer.dropped_nodes[0])
    print(f"[WRITER] Scan completed; beacon {node_id} confirmed in network storage")
    return node_id


if __name__ == "__main__":
    run_writer()
