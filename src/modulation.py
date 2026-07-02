"""QPSK modulation and demodulation."""

import numpy as np


SQRT2 = np.sqrt(2.0)
QPSK_MAPPING = {
    (0, 0): (1 + 1j) / SQRT2,
    (0, 1): (-1 + 1j) / SQRT2,
    (1, 1): (-1 - 1j) / SQRT2,
    (1, 0): (1 - 1j) / SQRT2,
}


def qpsk_modulate(bits):
    bit_list = [int(bit) & 1 for bit in bits]
    if len(bit_list) % 2:
        bit_list.append(0)
    symbols = [QPSK_MAPPING[(bit_list[idx], bit_list[idx + 1])] for idx in range(0, len(bit_list), 2)]
    return np.asarray(symbols, dtype=complex)


def qpsk_demodulate(symbols):
    bits = []
    for symbol in np.asarray(symbols, dtype=complex):
        if symbol.real >= 0 and symbol.imag >= 0:
            bits.extend([0, 0])
        elif symbol.real < 0 and symbol.imag >= 0:
            bits.extend([0, 1])
        elif symbol.real < 0 and symbol.imag < 0:
            bits.extend([1, 1])
        else:
            bits.extend([1, 0])
    return bits


modulate_qpsk = qpsk_modulate
qpsk_mapper = qpsk_modulate
modulate = qpsk_modulate
demodulate_qpsk = qpsk_demodulate
qpsk_demapper = qpsk_demodulate
demodulate = qpsk_demodulate
