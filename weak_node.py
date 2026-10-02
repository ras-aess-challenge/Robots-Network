import time
import math

class WeakNode:
    def __init__(self, node_id, x, y, timestamp, event, pod):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.timestamp = timestamp
        self.event = event
        self.pod = pod

    @classmethod
    def from_dict(cls, data):
        """Reconstructs a WeakNode from a dict received over the network
        (e.g. the Command Post's mission list), so there's one single
        source of truth for the decay formula instead of duplicating it."""
        return cls(
            node_id=data["node_id"],
            x=data["x"],
            y=data["y"],
            timestamp=data["timestamp"],
            event=data["event"],
            pod=data["pod"]
        )

    def current_pod(self, read_time=None, decay_rate=0.01):
        if read_time is None:
            read_time = time.time()
        elapsed = read_time - self.timestamp
        decayed = self.pod * math.exp(-decay_rate * elapsed)
        return decayed

    def read(self):
        return {
            "node_id": self.node_id,
            "x": self.x,
            "y": self.y,
            "timestamp": self.timestamp,
            "event": self.event,
            "pod": self.pod
        }


if __name__ == "__main__":
    node = WeakNode(
        node_id="WN001",
        x=120,
        y=80,
        timestamp=time.time() - 60,
        event="VICTIM",
        pod=0.92
    )
    print("Initial PoD:", node.pod)
    print("Current (decayed) PoD:", node.current_pod())