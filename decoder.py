import struct
from datetime import datetime
from typing import Dict, List, Any


def _decode_avl(data: bytes, offset: int, codec: int) -> List[Dict[str, Any]]:
    """
    Decode AVL records from Teltonika payload.
    :param data: The raw payload bytes.
    :param offset: Start position in payload.
    :param codec: Codec identifier.
    :return: List of decoded records.
    """
    records: List[Dict[str, Any]] = []
    count = data[offset]
    offset += 1
    for _ in range(count):
        ts_raw, = struct.unpack_from(
            ">Q", data, offset
        )
        offset += 8

        priority = data[offset]
        offset += 1

        lon, lat = struct.unpack_from(
            ">ii", data, offset
        )
        offset += 8

        alt, angle = struct.unpack_from(
            ">hh", data, offset
        )
        offset += 4

        sats = data[offset]
        speed, = struct.unpack_from(
            ">H", data, offset + 1
        )
        offset += 3

        record: Dict[str, Any] = {
            "timestamp": datetime.utcfromtimestamp(ts_raw / 1000).isoformat() + "Z",
            "priority": priority,
            "latitude": lat / 1e7,
            "longitude": lon / 1e7,
            "altitude": alt,
            "angle": angle,
            "satellites": sats,
            "speed": speed,
            "io": {}
        }

        # Event ID format depends on codec
        eid_fmt = ">B" if codec in (0x08, 0x0C, 0x0D, 0x0E) else ">H"
        eid = struct.unpack_from(eid_fmt, data, offset)[0]
        offset += struct.calcsize(eid_fmt)
        record["event_id"] = eid

        # Extended fields for codec 0x10
        if codec == 0x10:
            record["gen_type"] = data[offset]
            offset += 1

        # Total IO count format
        tot_fmt = ">B" if codec in (0x08, 0x0C, 0x0D, 0x0E) else ">H"
        total = struct.unpack_from(tot_fmt, data, offset)[0]
        offset += struct.calcsize(tot_fmt)

        # Decode IO elements
        for size in (1, 2, 4, 8):
            cnt = data[offset]
            offset += 1
            for _ in range(cnt):
                io_id = data[offset]
                offset += 1
                val_fmt = {1: ">B", 2: ">H", 4: ">I", 8: ">Q"}[size]
                val, = struct.unpack_from(val_fmt, data, offset)
                offset += size
                record["io"][str(io_id)] = val

        records.append(record)

    # Skip end marker
    offset += 1
    return records


def decode_teltonika(hex_str: str) -> Dict[str, Any]:
    """
    Decode a full Teltonika message from its hex string representation.
    Supports codecs: 0x08, 0x8E, 0x10 (AVL data), 0x0C (text), 0x0D (alarm text), 0x0E (IMEI text).

    :param hex_str: Hexadecimal string of the entire message.
    :return: Parsed dictionary with codec and records or text.
    """
    data = bytes.fromhex(hex_str)
    pre, length = struct.unpack_from(
        ">II", data, 0
    )
    payload = data[8:8 + length]
    codec = payload[0]
    result: Dict[str, Any] = {"codec": codec}

    if codec in (0x08, 0x8E, 0x10):
        result["records"] = _decode_avl(payload, 1, codec)
    elif codec == 0x0C:
        qty, typ = payload[1], payload[2]
        size, = struct.unpack_from(
            ">I", payload, 3
        )
        txt = payload[7:7 + size].decode(
            "ascii", errors="ignore"
        )
        result.update({"type": typ, "text": txt})
    elif codec == 0x0D:
        qty, typ = payload[1], payload[2]
        size, = struct.unpack_from(
            ">I", payload, 3
        )
        ts, = struct.unpack_from(
            ">I", payload, 7
        )
        txt = payload[11:11 + size - 4].decode(
            "ascii", errors="ignore"
        )
        result.update({"type": typ, "timestamp": ts, "text": txt})
    elif codec == 0x0E:
        qty, typ = payload[1], payload[2]
        size, = struct.unpack_from(
            ">I", payload, 3
        )
        imei_bytes = payload[7:15]
        imei = ''.join(f"{b:02X}" for b in imei_bytes)
        txt = payload[15:7 + size].decode(
            "ascii", errors="ignore"
        )
        result.update({"type": typ, "imei": imei, "text": txt})
    else:
        raise ValueError(f"Unsupported codec: {codec}")

    return result


if __name__ == "__main__":
    import json

    sample_hex = "00000000000000100C0106000000076765747374617475730100001F9A..."
    decoded = decode_teltonika(sample_hex)
    print(json.dumps(decoded, indent=2))
