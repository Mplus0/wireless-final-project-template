"""UTF-8 source coding helpers."""


def text_to_bits(text):
    data = str(text).encode("utf-8")
    bits = []
    for byte in data:
        for shift in range(7, -1, -1):
            bits.append((byte >> shift) & 1)
    return bits


def bits_to_text(bits):
    bit_list = [int(bit) & 1 for bit in bits]
    usable = len(bit_list) - (len(bit_list) % 8)
    data = bytearray()
    for idx in range(0, usable, 8):
        value = 0
        for bit in bit_list[idx : idx + 8]:
            value = (value << 1) | bit
        data.append(value)
    return bytes(data).decode("utf-8", errors="replace")


def source_encode(text):
    return text_to_bits(text)


def source_decode(bits):
    return bits_to_text(bits)


utf8_to_bits = text_to_bits
bits_to_utf8 = bits_to_text
encode_text = source_encode
decode_text = source_decode
