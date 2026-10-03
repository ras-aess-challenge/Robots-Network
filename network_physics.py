import math
import random

MAX_RANGE_M = 2000.0          # hard cutoff — beyond this, no link at all
DEGRADATION_START_M = 1400.0  # packet loss probability starts rising here


def distance_to_origin(x, y):
    return math.hypot(x, y)


def packet_loss_probability(distance):
    """0% loss below DEGRADATION_START_M, rising to 90% at MAX_RANGE_M."""
    if distance <= DEGRADATION_START_M:
        return 0.0
    if distance >= MAX_RANGE_M:
        return 1.0
    progress = (distance - DEGRADATION_START_M) / (MAX_RANGE_M - DEGRADATION_START_M)
    return min(0.9, progress * 0.9)


def attempt_transmission(x, y):
    """Returns (success, distance, loss_probability) for a beacon sent from (x, y)."""
    distance = distance_to_origin(x, y)

    if distance > MAX_RANGE_M:
        return False, distance, 1.0

    loss_prob = packet_loss_probability(distance)
    success = random.random() >= loss_prob
    return success, distance, loss_prob


if __name__ == "__main__":
    for test_x in [0, 500, 1000, 1500, 1800, 2000, 2500]:
        success, dist, loss_prob = attempt_transmission(test_x, 0)
        status = "OK" if success else "LOST/OUT-OF-RANGE"
        print(f"x={test_x:5}m -> distance={dist:7.1f}m, loss_prob={loss_prob:.2f}, result={status}")