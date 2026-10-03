import time
import math

class Executor:
    def __init__(self, executor_id, read_range=5, speed=1.0):
        self.executor_id = executor_id
        self.read_range = read_range
        self.speed = speed  # meters per step
        self.x = 0
        self.y = 0

    def move_to(self, x, y):
        """Instant teleport — kept for quick tests, but navigate_to is now preferred."""
        self.x = x
        self.y = y
        print(f"[{self.executor_id}] Moved to ({x}, {y})")

    def navigate_to(self, target_x, target_y, step_delay=0.3):
        """Moves step by step toward (target_x, target_y) at self.speed per step,
        printing progress — simulates real navigation instead of teleporting."""
        print(f"[{self.executor_id}] Navigating from ({self.x:.1f}, {self.y:.1f}) "
              f"toward ({target_x:.1f}, {target_y:.1f})")

        while True:
            dx = target_x - self.x
            dy = target_y - self.y
            distance_remaining = math.hypot(dx, dy)

            if distance_remaining <= self.speed:
                self.x = target_x
                self.y = target_y
                print(f"[{self.executor_id}] Arrived at ({self.x:.1f}, {self.y:.1f})")
                break

            # move one step toward the target
            ratio = self.speed / distance_remaining
            self.x += dx * ratio
            self.y += dy * ratio
            print(f"[{self.executor_id}] ... at ({self.x:.1f}, {self.y:.1f}), "
                  f"{distance_remaining - self.speed:.1f}m remaining")

            if step_delay:
                time.sleep(step_delay)

    def pick_nearest_target(self, node_list):
        """Chooses the closest beacon from the mission list as the navigation target."""
        if not node_list:
            return None

        nearest = min(
            node_list,
            key=lambda n: math.hypot(n.x - self.x, n.y - self.y)
        )
        return nearest

    def scan_for_nodes(self, node_list):
        readings = []
        for node in node_list:
            distance = math.hypot(node.x - self.x, node.y - self.y)
            if distance <= self.read_range:
                readings.append(self.read_node(node))
        return readings

    def read_node(self, node):
        decayed_pod = node.current_pod()
        print(f"[{self.executor_id}] Read {node.node_id} — "
              f"event: {node.event}, PoD: {decayed_pod:.3f} "
              f"(initial: {node.pod}), coords: ({node.x:.1f}, {node.y:.1f})")
        return {**node.read(), "current_pod": decayed_pod}


if __name__ == "__main__":
    from writer import Writer

    writer = Writer("WRITER_1", spatial_limit=10.0)
    writer.move_to(x=35, y=0, event="VICTIM", pod=0.9)

    executor = Executor("EXECUTOR_1", read_range=5, speed=2.0)
    target = executor.pick_nearest_target(writer.dropped_nodes)

    if target:
        executor.navigate_to(target.x, target.y)
        executor.scan_for_nodes(writer.dropped_nodes)
    else:
        print(f"[{executor.executor_id}] No targets available.")
