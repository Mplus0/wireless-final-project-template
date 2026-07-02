"""PN-sequence XOR scrambling."""

import numpy as np


def scramble(bits, seed=2026):
    bit_array = np.asarray([int(bit) & 1 for bit in bits], dtype=np.uint8)
    rng = np.random.default_rng(seed)
    pn = rng.integers(0, 2, size=len(bit_array), dtype=np.uint8)
    return np.bitwise_xor(bit_array, pn).astype(int).tolist()


def descramble(bits, seed=2026):
    return scramble(bits, seed=seed)


scramble_bits = scramble
descramble_bits = descramble
encrypt = scramble
decrypt = descramble
encrypt_bits = scramble
decrypt_bits = descramble
