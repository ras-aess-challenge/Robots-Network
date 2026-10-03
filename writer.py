import time
import math
from weak_node import WeakNode

class Writer:
    def __init__(self, writer_id, spatial_limit=10.0, temporal_limit=30.0):
        self.writer_id = writer_id
        self.dropped_nodes = []
        self.x = 0
        self.y = 0
        self.last_drop_x = 0
        self.last_drop_y = 0
        self.last_drop_time = time.time()
        self.spatial_limit = spatial_limit
        self.temporal_limit = temporal_limit
        self.alive = True

    def drop_node(self, event, pod):
        if not self.alive:
            print(f"[{self.writer_id}] Cannot drop — writer is DEAD")
            return None

        # Kinematic Invariant: velocity must be 0.0 m/s during write/verify cycle
        node_id = f"WN{len(self.dropped_nodes)+1:03d}"
        node = WeakNode(node_id, self.x, self.y, time.time(), event, pod)
        self.dropped_nodes.append(node)
        self.last_drop_x = self.x
        self.last_drop_y = self.y
        self.last_drop_time = time.time()
        print(f"[{self.writer_id}] Halted (v=0.0 m/s) — Dropped {node_id} "
              f"at ({self.x:.1f}, {self.y:.1f}) — event: {event}")
        return node

    def die(self):
        """Simulate battery removed / catastrophic attrition (spec Section 8, Step 2)."""
        self.alive = False
        print(f"[{self.writer_id}] ATTRITION — all active radios cease. Writer is dead.")

    def move_to(self, x, y, event="NONE", pod=0.5, step_delay=0):
        if not self.alive:
            print(f"[{self.writer_id}] Cannot move — writer is DEAD")
            return

        steps = 20
        start_x, start_y = self.x, self.y
        for i in range(1, steps + 1):
            if not self.alive:
                print(f"[{self.writer_id}] Movement interrupted — writer died mid-path")
                return

            self.x = start_x + (x - start_x) * i / steps
            self.y = start_y + (y - start_y) * i / steps

            if step_delay:
                time.sleep(step_delay)

            dist_since_drop = math.hypot(self.x - self.last_drop_x, self.y - self.last_drop_y)
            time_since_drop = time.time() - self.last_drop_time

            if dist_since_drop >= self.spatial_limit:
                print(f"[{self.writer_id}] RTA trigger: spatial limit reached")
                self.drop_node(event=event, pod=pod)
            elif time_since_drop >= self.temporal_limit:
                print(f"[{self.writer_id}] RTA trigger: temporal limit reached")
                self.drop_node(event=event, pod=pod)


if __name__ == "__main__":
    writer = Writer("WRITER_1", spatial_limit=10.0, temporal_limit=30.0)
    writer.move_to(x=35, y=0, event="VICTIM", pod=0.9)

    writer.die()  # simulate battery removal after mission
    writer.move_to(x=50, y=0, event="VICTIM", pod=0.9)  # should fail — writer is dead
    writer.drop_node(event="VICTIM", pod=0.9)            # should also fail

    print(f"Total tags dropped: {len(writer.dropped_nodes)}")