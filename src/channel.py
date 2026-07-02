"""Wireless channel models."""

import numpy as np


def awgn(symbols, snr_db=12, seed=2026):
    signal = np.asarray(symbols, dtype=complex)
    if signal.size == 0:
        return signal.copy()
    signal_power = float(np.mean(np.abs(signal) ** 2))
    snr_linear = 10 ** (float(snr_db) / 10.0)
    noise_power = signal_power / snr_linear
    rng = np.random.default_rng(seed)
    scale = np.sqrt(noise_power / 2.0)
    noise = rng.normal(0.0, scale, size=signal.shape) + 1j * rng.normal(0.0, scale, size=signal.shape)
    return signal + noise


awgn_channel = awgn
add_awgn = awgn
add_noise = awgn
