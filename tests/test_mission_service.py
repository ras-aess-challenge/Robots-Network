import threading
import time
import unittest
from unittest.mock import patch

from mission_service import MissionController

BEACON = {"node_id": "WN-test", "x": 10.5, "y": 0, "timestamp": time.time(), "event": "VICTIM", "pod": 0.9}


class MissionServiceTests(unittest.TestCase):
    def test_selected_beacon_is_executed_and_read(self):
        service = MissionController()
        with patch('mission_service.get_mission', return_value=[BEACON]), patch.dict('os.environ', {"EXECUTOR_STEP_DELAY": "0"}):
            service.assign({"id": "selected", "beaconId": "WN-test"})
            end = time.monotonic() + 2
            while service.snapshot()['mission']['status'] != 'done' and time.monotonic() < end:
                time.sleep(0.01)
        result = service.snapshot()
        self.assertEqual(result['mission']['status'], 'done')
        self.assertEqual(result['pos']['x'], 10.5)
        self.assertEqual(result['mission']['readings'][0]['node_id'], 'WN-test')
        self.assertEqual(service.assign({"id": "selected", "beaconId": "WN-test"})['status'], 'done')

    def test_unknown_beacon_and_malformed_assignment_fail(self):
        service = MissionController()
        with self.assertRaises(ValueError):
            service.assign({})
        with patch('mission_service.get_mission', return_value=[]):
            with self.assertRaises(ValueError):
                service.assign({"id": "missing", "beaconId": "unknown"})

    def test_busy_executor_and_cancellation(self):
        service = MissionController()
        running, stopped = threading.Event(), threading.Event()
        def navigate(*args, should_cancel, **kwargs):
            running.set()
            self.assertTrue(service.cancelled.wait(2))
            stopped.set()
            raise RuntimeError('cancelled')
        with patch('mission_service.get_mission', return_value=[BEACON]), patch.object(service.robot, 'navigate_to', side_effect=navigate):
            service.assign({"id": "cancel", "beaconId": "WN-test"})
            self.assertTrue(running.wait(2))
            with self.assertRaises(RuntimeError):
                service.assign({"id": "other", "beaconId": "WN-test"})
            service.cancel('cancel')
            self.assertTrue(stopped.wait(2))
            end = time.monotonic() + 2
            while service.snapshot()['mission']['status'] != 'cancelled' and time.monotonic() < end:
                time.sleep(0.01)
        self.assertEqual(service.snapshot()['mission']['status'], 'cancelled')
