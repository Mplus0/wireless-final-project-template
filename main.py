"""Command-line entry point for the wireless final project."""

from __future__ import annotations

import argparse
import json
import math
from difflib import SequenceMatcher
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.channel import awgn
from src.channel_coding import REPETITION_FACTOR, channel_decode, channel_encode
from src.framing import PREAMBLE_BITS, build_frame, parse_frame
from src.modulation import qpsk_demodulate, qpsk_modulate
from src.scramble import descramble, scramble
from src.source import source_decode, source_encode
from src.synchronization import synchronize


def parse_args():
    parser = argparse.ArgumentParser(description="Wireless baseband simulation")
    parser.add_argument("--input", required=True, help="Input UTF-8 text file")
    parser.add_argument("--output", required=True, help="Output recovered text file")
    parser.add_argument("--snr", type=float, default=12.0, help="SNR in dB")
    parser.add_argument("--seed", type=int, default=2026, help="Random seed")
    parser.add_argument("--mod", default="qpsk", help="Modulation, currently qpsk")
    parser.add_argument("--channel", default="awgn", help="Channel, currently awgn")
    return parser.parse_args()


def text_match_rate(reference, recovered):
    if reference == recovered:
        return 1.0
    return float(SequenceMatcher(None, reference, recovered).ratio())


def bit_error_rate(reference_bits, recovered_bits):
    length = min(len(reference_bits), len(recovered_bits))
    if len(reference_bits) == 0:
        return 0.0
    errors = sum(int(a) != int(b) for a, b in zip(reference_bits[:length], recovered_bits[:length]))
    errors += abs(len(reference_bits) - len(recovered_bits))
    return errors / len(reference_bits)


def make_prefix_symbols(seed, offset):
    rng = np.random.default_rng(seed + 17)
    prefix_bits = rng.integers(0, 2, size=offset * 2).astype(int).tolist()
    return qpsk_modulate(prefix_bits)


def choose_sync_offset(seed):
    rng = np.random.default_rng(seed + 99)
    return int(rng.integers(0, 129))


def plot_constellation(path, symbols, snr_db):
    fig, ax = plt.subplots(figsize=(5, 5), dpi=140)
    sample = np.asarray(symbols[: min(len(symbols), 2000)], dtype=complex)
    ax.scatter(sample.real, sample.imag, s=8, alpha=0.55, label="received")
    ideal = qpsk_modulate([0, 0, 0, 1, 1, 1, 1, 0])
    ax.scatter(ideal.real, ideal.imag, s=45, marker="x", color="black", label="ideal")
    ax.axhline(0, color="#888888", linewidth=0.8)
    ax.axvline(0, color="#888888", linewidth=0.8)
    ax.set_title(f"QPSK constellation, SNR={snr_db:g} dB")
    ax.set_xlabel("In-phase")
    ax.set_ylabel("Quadrature")
    ax.grid(True, alpha=0.25)
    ax.set_aspect("equal", adjustable="box")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def theoretical_qpsk_ber(snr_db_values):
    values = []
    for snr_db in snr_db_values:
        snr_linear = 10 ** (snr_db / 10.0)
        values.append(0.5 * math.erfc(math.sqrt(snr_linear / 2.0)))
    return values


def plot_ber_curve(path, current_snr, current_ber):
    snrs = np.arange(0, 15, 2)
    bers = theoretical_qpsk_ber(snrs)
    fig, ax = plt.subplots(figsize=(6, 4), dpi=140)
    ax.semilogy(snrs, bers, marker="o", label="theoretical QPSK")
    ax.semilogy([current_snr], [max(current_ber, 1e-6)], marker="s", markersize=8, label="this run")
    ax.set_title("BER-SNR curve")
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("BER")
    ax.grid(True, which="both", alpha=0.3)
    ax.set_ylim(1e-6, 1)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_sync_peak(path, peak_values, start_index):
    fig, ax = plt.subplots(figsize=(6, 4), dpi=140)
    values = np.asarray(peak_values, dtype=float)
    if values.size:
        ax.plot(values, linewidth=1.2)
        ax.axvline(start_index, color="red", linestyle="--", label=f"start={start_index}")
    ax.set_title("Synchronization correlation peak")
    ax.set_xlabel("Candidate symbol index")
    ax.set_ylabel("Correlation magnitude")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def run_pipeline(input_path, output_path, snr_db, seed, modulation, channel_name):
    if modulation.lower() != "qpsk":
        raise ValueError("Only qpsk modulation is supported by the base system")
    if channel_name.lower() != "awgn":
        raise ValueError("Only awgn channel is supported by the base system")

    input_path = Path(input_path)
    output_path = Path(output_path)
    results_dir = output_path.parent
    results_dir.mkdir(parents=True, exist_ok=True)

    original_text = input_path.read_text(encoding="utf-8")
    source_bits = source_encode(original_text)
    scrambled_bits = scramble(source_bits, seed=seed)
    coded_bits = channel_encode(scrambled_bits)
    frame_bits = build_frame(coded_bits, original_payload_length=len(source_bits))
    tx_symbols = qpsk_modulate(frame_bits)

    sync_offset = choose_sync_offset(seed)
    prefix_symbols = make_prefix_symbols(seed, sync_offset)
    tx_with_offset = np.concatenate([prefix_symbols, tx_symbols])
    rx_symbols = awgn(tx_with_offset, snr_db=snr_db, seed=seed)

    preamble_symbols = qpsk_modulate(PREAMBLE_BITS)
    sync_result = synchronize(rx_symbols, preamble=preamble_symbols)
    sync_start = int(sync_result["start_index"])
    aligned_symbols = rx_symbols[sync_start : sync_start + len(tx_symbols)]

    failure_reason = ""
    recovered_text = ""
    recovered_source_bits = []
    checksum_pass = False
    parsed = {}

    try:
        demod_bits = qpsk_demodulate(aligned_symbols)
        parsed = parse_frame(demod_bits)
        checksum_pass = bool(parsed.get("checksum_pass", False))
        decoded_scrambled_bits = channel_decode(parsed["payload"])
        payload_length = int(parsed.get("length", len(source_bits)))
        decoded_scrambled_bits = decoded_scrambled_bits[:payload_length]
        recovered_source_bits = descramble(decoded_scrambled_bits, seed=seed)[:payload_length]
        recovered_text = source_decode(recovered_source_bits)
    except Exception as exc:  # pragma: no cover - defensive runtime path
        failure_reason = f"receiver_error: {exc}"
        recovered_source_bits = []
        recovered_text = ""

    output_path.write_text(recovered_text, encoding="utf-8")

    ber = bit_error_rate(source_bits, recovered_source_bits)
    match_rate = text_match_rate(original_text, recovered_text)
    frame_error = 0.0 if recovered_text == original_text and checksum_pass else 1.0
    if not failure_reason and recovered_text != original_text:
        failure_reason = "bit_errors_or_checksum_failure"
    if not failure_reason:
        failure_reason = "none"

    metrics = {
        "snr_db": float(snr_db),
        "seed": int(seed),
        "modulation": modulation.lower(),
        "channel": channel_name.lower(),
        "payload_bits": len(source_bits),
        "coded_bits": len(coded_bits),
        "frame_bits": len(frame_bits),
        "coding_rate": 1.0 / REPETITION_FACTOR,
        "ber": float(ber),
        "fer": float(frame_error),
        "text_match_rate": float(match_rate),
        "checksum_pass": bool(checksum_pass),
        "crc_pass": bool(checksum_pass),
        "sync_start_index": int(sync_start),
        "sync_offset_symbols": int(sync_offset),
        "sync_error_symbols": int(sync_start - sync_offset),
        "failure_reason": failure_reason,
    }

    metrics_path = results_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    plot_constellation(results_dir / "constellation.png", aligned_symbols, snr_db)
    plot_ber_curve(results_dir / "ber_curve.png", snr_db, ber)
    plot_sync_peak(results_dir / "sync_peak.png", sync_result.get("peak_values", []), sync_start)

    return metrics


def main():
    args = parse_args()
    metrics = run_pipeline(args.input, args.output, args.snr, args.seed, args.mod, args.channel)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
