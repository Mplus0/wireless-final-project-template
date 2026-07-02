"""Frame construction and parsing."""

import zlib


PREAMBLE_BITS = [
    1, 0, 0, 1, 0, 0, 0, 0,
    1, 0, 1, 1, 1, 1, 1, 0,
    1, 1, 0, 0, 0, 1, 1, 1,
    0, 1, 1, 1, 0, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 0, 0, 0, 1, 1, 0,
    0, 0, 1, 0, 0, 0, 0, 1,
    0, 0, 1, 0, 1, 0, 1, 1,
]
UINT_BITS = 32


def _to_bit_list(bits):
    return [int(bit) & 1 for bit in bits]


def int_to_bits(value, width=UINT_BITS):
    value = int(value)
    return [(value >> shift) & 1 for shift in range(width - 1, -1, -1)]


def bits_to_int(bits):
    value = 0
    for bit in bits:
        value = (value << 1) | (int(bit) & 1)
    return value


def bits_to_bytes(bits):
    bit_list = _to_bit_list(bits)
    padded = list(bit_list)
    while len(padded) % 8:
        padded.append(0)
    data = bytearray()
    for idx in range(0, len(padded), 8):
        value = 0
        for bit in padded[idx : idx + 8]:
            value = (value << 1) | bit
        data.append(value)
    return bytes(data)


def crc32_bits(bits):
    return zlib.crc32(bits_to_bytes(bits)) & 0xFFFFFFFF


def build_frame(payload_bits, original_payload_length=None, **kwargs):
    payload = _to_bit_list(payload_bits)
    if original_payload_length is None:
        original_payload_length = kwargs.get("length", len(payload))
    frame = []
    frame.extend(PREAMBLE_BITS)
    frame.extend(int_to_bits(int(original_payload_length), UINT_BITS))
    frame.extend(int_to_bits(len(payload), UINT_BITS))
    frame.extend(payload)
    frame.extend(int_to_bits(crc32_bits(payload), UINT_BITS))
    return frame


def _find_preamble(bits):
    limit = len(bits) - len(PREAMBLE_BITS) + 1
    for idx in range(max(0, limit)):
        if bits[idx : idx + len(PREAMBLE_BITS)] == PREAMBLE_BITS:
            return idx
    return 0


def parse_frame(frame_bits):
    bits = _to_bit_list(frame_bits)
    start = _find_preamble(bits)
    cursor = start + len(PREAMBLE_BITS)
    if len(bits) < cursor + 2 * UINT_BITS:
        raise ValueError("Frame is too short to contain length fields")

    source_length = bits_to_int(bits[cursor : cursor + UINT_BITS])
    cursor += UINT_BITS
    payload_length = bits_to_int(bits[cursor : cursor + UINT_BITS])
    cursor += UINT_BITS

    payload = bits[cursor : cursor + payload_length]
    cursor += payload_length
    received_crc_bits = bits[cursor : cursor + UINT_BITS]
    received_crc = bits_to_int(received_crc_bits) if len(received_crc_bits) == UINT_BITS else None
    computed_crc = crc32_bits(payload)

    return {
        "preamble": PREAMBLE_BITS,
        "length": source_length,
        "payload_bits": payload_length,
        "payload_length": payload_length,
        "payload": payload,
        "checksum": computed_crc,
        "crc": computed_crc,
        "received_crc": received_crc,
        "checksum_pass": received_crc == computed_crc,
        "start_bit_index": start,
    }


frame_build = build_frame
create_frame = build_frame
make_frame = build_frame
frame_parse = parse_frame
extract_frame = parse_frame
decode_frame = parse_frame
