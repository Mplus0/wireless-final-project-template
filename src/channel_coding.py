"""Simple repetition channel coding."""


REPETITION_FACTOR = 3


def channel_encode(bits, repeat=REPETITION_FACTOR):
    encoded = []
    for bit in bits:
        encoded.extend([int(bit) & 1] * int(repeat))
    return encoded


def channel_decode(bits, repeat=REPETITION_FACTOR):
    repeat = int(repeat)
    bit_list = [int(bit) & 1 for bit in bits]
    decoded = []
    for idx in range(0, len(bit_list) - len(bit_list) % repeat, repeat):
        group = bit_list[idx : idx + repeat]
        decoded.append(1 if sum(group) >= (repeat / 2) else 0)
    return decoded


encode = channel_encode
decode = channel_decode
encode_bits = channel_encode
decode_bits = channel_decode
fec_encode = channel_encode
fec_decode = channel_decode
