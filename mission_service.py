"""Private HTTP adapter for dashboard-assigned missions using the existing Executor."""
import json
import os
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from executor import Executor
from executor_client import get_mission
from weak_node import WeakNode


class MissionController:
    def __init__(self):
        self.lock = threading.RLock()
        self.robot = Executor("executor", read_range=5, speed=2.0)
        self.current = None
        self.cancelled = threading.Event()

    def snapshot(self):
        with self.lock:
            return {"pos": {"x": self.robot.x, "y": self.robot.y},
                    "mission": dict(self.current) if self.current else None}

    def assign(self, payload):
        if not isinstance(payload, dict) or not isinstance(payload.get("id"), str) or not isinstance(payload.get("beaconId"), str):
            raise ValueError("id and beaconId are required")
        with self.lock:
            if self.current and self.current["id"] == payload["id"]:
                return dict(self.current)
            if self.current and self.current["status"] in ("pending", "active"):
                raise RuntimeError("Executor already has an active mission")
            nodes = [WeakNode.from_dict(b) for b in get_mission()]
            target = next((n for n in nodes if n.node_id == payload["beaconId"]), None)
            if target is None:
                raise ValueError("Unknown beacon")
            now = datetime.now(timezone.utc).isoformat()
            self.current = {"id": payload["id"], "targetRobot": "executor",
                            "objective": str(payload.get("objective", "Inspect beacon"))[:280],
                            "target": {"beaconId": target.node_id, "pos": {"x": target.x, "y": target.y}},
                            "status": "pending", "ts": now, "updatedAt": now}
            self.cancelled.clear()
            initial = dict(self.current)
            threading.Thread(target=self._execute, args=(target, nodes), daemon=True).start()
            return initial

    def _status(self, value):
        self.current["status"] = value
        self.current["updatedAt"] = datetime.now(timezone.utc).isoformat()

    def _execute(self, target, nodes):
        with self.lock:
            self._status("active")
        try:
            self.robot.navigate_to(target.x, target.y,
                                   step_delay=float(os.getenv("EXECUTOR_STEP_DELAY", "0.3")),
                                   should_cancel=self.cancelled.is_set)
            with self.lock:
                if self.cancelled.is_set():
                    self._status("cancelled")
                else:
                    self.current["readings"] = self.robot.scan_for_nodes(nodes)
                    self._status("done")
        except Exception as exc:
            with self.lock:
                self._status("cancelled" if self.cancelled.is_set() else "failed")
            print(f"[EXECUTOR_SERVICE] Mission stopped: {type(exc).__name__}")

    def cancel(self, mission_id):
        with self.lock:
            if not self.current or self.current["id"] != mission_id:
                raise ValueError("Unknown mission")
            if self.current["status"] in ("pending", "active"):
                self.cancelled.set()
            return dict(self.current)


controller = MissionController()


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self.respond(200, {"status": "ok"})
        elif self.path == "/state":
            self.respond(200, controller.snapshot())
        else:
            self.respond(404, {"error": "Not found"})

    def do_POST(self):
        self.connection.settimeout(5)
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 8192:
                raise ValueError("Invalid request size")
            body = json.loads(self.rfile.read(size))
            if self.path == "/missions":
                self.respond(202, controller.assign(body))
            elif self.path == "/cancel" and isinstance(body, dict):
                self.respond(200, controller.cancel(body.get("missionId")))
            else:
                self.respond(404, {"error": "Not found"})
        except (ValueError, TypeError, KeyError):
            self.respond(400, {"error": "Invalid mission request or unknown beacon"})
        except RuntimeError:
            self.respond(409, {"error": "Executor busy"})
        except OSError:
            self.respond(503, {"error": "Network unavailable"})


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
