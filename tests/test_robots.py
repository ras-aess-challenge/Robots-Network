import math
import time
import unittest
from unittest.mock import patch

from beacon_codec import pack_beacon, unpack_beacon
from executor import Executor
from executor_client import get_mission, run_executor
from network_physics import attempt_transmission, packet_loss_probability
from weak_node import WeakNode
from writer import Writer
from writer_client import send_node


class RobotTests(unittest.TestCase):
    def test_scan_drop_and_attrition(self):
        writer = Writer("test")
        writer.move_to(15, 0, event="VICTIM", pod=0.9)
        self.assertEqual(len(writer.dropped_nodes), 1)
        node = writer.dropped_nodes[0]
        self.assertEqual((node.x, node.y, node.event), (10.5, 0, "VICTIM"))
        writer.die()
        writer.move_to(30, 0)
        self.assertIsNone(writer.drop_node("HAZARD", 0.5))
        self.assertEqual(len(writer.dropped_nodes), 1)

    def test_codec_and_decay(self):
        node = WeakNode("one", -12.34, 56.78, 123, "VICTIM", 0.9)
        decoded = unpack_beacon(pack_beacon(node.x, node.y, node.timestamp, node.event, node.pod))
        self.assertEqual((decoded["x"], decoded["y"]), (-12.34, 56.78))
        self.assertAlmostEqual(node.current_pod(read_time=223), 0.9 * math.exp(-1))

    def test_radio_range(self):
        self.assertEqual(packet_loss_probability(15), 0)
        self.assertEqual(attempt_transmission(2500, 0), (False, 2500, 1))

    def test_writer_checks_acknowledgement(self):
        node = WeakNode("test", 10.5, 0, 123, "VICTIM", 0.9)
        with patch("writer_client.request", return_value=b"RECEIVED WN-123"):
            self.assertEqual(send_node(node), "WN-123")
        with patch("writer_client.request", return_value=b"STORED"):
            with self.assertRaises(RuntimeError):
                send_node(node)
        with patch("writer_client.attempt_transmission", return_value=(False, 10.5, 0.5)):
            with self.assertRaises(RuntimeError):
                send_node(node)

    def test_mission_validation_and_empty_failure(self):
        with patch("executor_client.request", return_value=b"{}"):
            with self.assertRaises(ValueError):
                get_mission()
        with patch("executor_client.request", return_value=b'[{}]'):
            with self.assertRaises(KeyError):
                get_mission()
        with patch("executor_client.request", return_value=b"[]"):
            with self.assertRaises(RuntimeError):
                run_executor()

    def test_navigation_and_read(self):
        node = WeakNode("test", 10.5, 0, time.time(), "VICTIM", 0.9)
        robot = Executor("test", speed=2)
        robot.navigate_to(node.x, node.y, step_delay=0)
        readings = robot.scan_for_nodes([node])
        self.assertEqual((robot.x, robot.y), (node.x, node.y))
        self.assertEqual(readings[0]["node_id"], "test")
        self.assertLessEqual(readings[0]["current_pod"], 0.9)
