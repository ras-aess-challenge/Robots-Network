"""Run both real CLI entry points against live containers on an isolated mission store."""
import json
import os
import subprocess
import sys
import unittest

from executor_client import get_mission


class FullSystemTests(unittest.TestCase):
    def test_writer_network_executor(self):
        self.assertEqual(get_mission(), [], "Use a fresh test volume; this test never clears mission data")
        writer = subprocess.run([sys.executable, "writer_client.py"], capture_output=True, text=True, timeout=20)
        print(writer.stdout, end="")
        self.assertEqual(writer.returncode, 0, writer.stderr)
        self.assertIn("confirmed in network storage", writer.stdout)
        mission = get_mission()
        self.assertEqual(len(mission), 1)
        beacon = mission[0]
        self.assertEqual((beacon["x"], beacon["y"], beacon["event"]), (10.5, 0, "VICTIM"))
        self.assertAlmostEqual(beacon["pod"], 0.95, places=6)
        self.assertIn("lat", beacon)
        self.assertIn("lon", beacon)
        self.assertIn(beacon["node_id"], writer.stdout)

        executor = subprocess.run([sys.executable, "executor_client.py"], capture_output=True, text=True, timeout=20)
        print(executor.stdout, end="")
        self.assertEqual(executor.returncode, 0, executor.stderr)
        marker = "[EXECUTOR] Mission completed: "
        line = next(line for line in executor.stdout.splitlines() if line.startswith(marker))
        result = json.loads(line[len(marker):])
        self.assertEqual(result["target_id"], beacon["node_id"])
        self.assertEqual((result["x"], result["y"]), (beacon["x"], beacon["y"]))
        self.assertEqual(result["readings"][0]["event"], "VICTIM")
        self.assertGreater(result["readings"][0]["current_pod"], 0)
        self.assertEqual(get_mission(), mission, "Executor must not delete stored beacons")

    def test_wrong_secret_fails_job(self):
        environment = {**os.environ, "SHARED_SECRET": "wrong-key-" * 8}
        process = subprocess.run([sys.executable, "executor_client.py"], env=environment, capture_output=True, text=True, timeout=20)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("authentication failed", process.stderr)
