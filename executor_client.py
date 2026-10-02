import json
import os

from executor import Executor
from weak_node import WeakNode
from network_client import request
from security_config import MSG_TYPE_MISSION_REQUEST


def get_mission():
    response = request(MSG_TYPE_MISSION_REQUEST)
    beacons = json.loads(response.decode("utf-8"))
    if not isinstance(beacons, list):
        raise ValueError("Mission must be a list of beacons")
    # Validate records before navigating, rather than failing halfway through.
    for beacon in beacons:
        WeakNode.from_dict(beacon)
    print(f"[EXECUTOR] Received mission: {len(beacons)} beacon(s)")
    return beacons


def run_executor():
    nodes = [WeakNode.from_dict(b) for b in get_mission()]
    executor = Executor("EXECUTOR_1", read_range=5, speed=2.0)
    target = executor.pick_nearest_target(nodes)
    if target is None:
        raise RuntimeError("No beacons available to navigate to")
    step_delay = float(os.environ.get("EXECUTOR_STEP_DELAY", "0.3"))
    if step_delay < 0:
        raise ValueError("EXECUTOR_STEP_DELAY must not be negative")
    executor.navigate_to(target.x, target.y, step_delay=step_delay)
    readings = executor.scan_for_nodes(nodes)
    if not any(reading["node_id"] == target.node_id for reading in readings):
        raise RuntimeError("Executor did not read the target beacon")
    result = {
        "target_id": target.node_id,
        "x": executor.x,
        "y": executor.y,
        "readings": readings,
    }
    print("[EXECUTOR] Mission completed: " + json.dumps(result))
    return result


if __name__ == "__main__":
    run_executor()
