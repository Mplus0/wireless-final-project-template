"""Frame synchronization by preamble correlation."""

import numpy as np


def default_preamble_symbols():
    from .framing import PREAMBLE_BITS
    from .modulation import qpsk_modulate

    return qpsk_modulate(PREAMBLE_BITS)


def synchronize(received_symbols, preamble=None):
    received = np.asarray(received_symbols, dtype=complex)
    known = default_preamble_symbols() if preamble is None else np.asarray(preamble, dtype=complex)
    if len(received) < len(known):
        return {"start_index": 0, "sync_start_index": 0, "peak_values": []}
    corr = np.abs(np.correlate(received, known, mode="valid"))
    start = int(np.argmax(corr))
    return {
        "start_index": start,
        "sync_start_index": start,
        "index": start,
        "peak_value": float(corr[start]),
        "peak_values": corr.tolist(),
    }


def detect_frame_start(received_symbols, preamble=None):
    return synchronize(received_symbols, preamble=preamble)


def find_preamble(received_symbols, preamble=None):
    return synchronize(received_symbols, preamble=preamble)


sync = synchronize
