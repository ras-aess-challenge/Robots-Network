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
    print("[WRITER] Deploying into unknown zone...")
    
    # Event 1: Drop a Victim tag
    writer.move_to(x=10.5, y=0, event="VICTIM", pod=0.95)
    
    # Event 2: Drop a Fire tag 5 meters later
    writer.move_to(x=15.5, y=2.0, event="FIRE", pod=0.85)

    if not writer.dropped_nodes:
        raise RuntimeError("No beacon was dropped")
        
    # Send both to the ONA (Simulating the 5m Strong Node burst)
    for node in writer.dropped_nodes:
        node_id = send_node(node)
        print(f"[WRITER] Scan completed; beacon {node_id} confirmed in network storage")
        
    return node_id

if __name__ == "__main__":
    run_writer()
