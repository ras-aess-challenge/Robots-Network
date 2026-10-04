import struct
import time

EVENT_CODES = {
    "NONE": 0,
    "VICTIM": 1,
    "FIRE": 2,      
    "HAZARD": 3,
    "DEBRIS": 4,
}
EVENT_NAMES = {code: name for name, code in EVENT_CODES.items()}

PAYLOAD_SIZE = 16  # bytes, per spec


def pack_beacon(x, y, timestamp, event, pod):
    """
    Packs beacon data into the spec's 16-byte CRDT payload.
    x, y are in meters, converted to centimeters for 3-byte signed precision
    (range: about +/- 83.8 km, far more than needed here).
    timestamp is Unix time in seconds, truncated to fit 4 bytes.
    """
    ts = int(timestamp) & 0xFFFFFFFF
    x_cm = int(round(x * 100))
    y_cm = int(round(y * 100))

    if not (-8_388_608 <= x_cm <= 8_388_607):
        raise ValueError(f"x={x} out of encodable range")
    if not (-8_388_608 <= y_cm <= 8_388_607):
        raise ValueError(f"y={y} out of encodable range")

    event_code = EVENT_CODES.get(event, 0)

    payload = b""
    payload += struct.pack(">I", ts)                 # 4 bytes
    payload += x_cm.to_bytes(3, "big", signed=True)   # 3 bytes
    payload += y_cm.to_bytes(3, "big", signed=True)   # 3 bytes
    payload += struct.pack(">H", event_code)          # 2 bytes
    payload += struct.pack(">f", pod)                 # 4 bytes

    assert len(payload) == PAYLOAD_SIZE, f"Payload is {len(payload)} bytes, expected {PAYLOAD_SIZE}"
    return payload


def unpack_beacon(data: bytes):
    if len(data) != PAYLOAD_SIZE:
        raise ValueError(f"Invalid payload size: {len(data)} bytes, expected {PAYLOAD_SIZE}")

    ts = struct.unpack(">I", data[0:4])[0]
    x_cm = int.from_bytes(data[4:7], "big", signed=True)
    y_cm = int.from_bytes(data[7:10], "big", signed=True)
    event_code = struct.unpack(">H", data[10:12])[0]
    pod = struct.unpack(">f", data[12:16])[0]

    return {
        "timestamp": ts,
        "x": x_cm / 100.0,
        "y": y_cm / 100.0,
        "event": EVENT_NAMES.get(event_code, "UNKNOWN"),
        "pod": pod,
    }


if __name__ == "__main__":
    packed = pack_beacon(x=10.5, y=0.0, timestamp=time.time(), event="VICTIM", pod=0.9)
    print(f"Packed payload ({len(packed)} bytes): {packed.hex()}")

    unpacked = unpack_beacon(packed)
    print("Unpacked:", unpacked)
