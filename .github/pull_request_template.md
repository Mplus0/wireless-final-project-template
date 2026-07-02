## Student Information

- Student ID: 2024280057
- Name: 孟佳霖
- GitHub username: Mplus0
- Fork repository URL: https://github.com/Mplus0/wireless-final-project-template.git
- Branch: main
- PR number: GitHub will assign this after the Pull Request is created. You may leave it blank first and fill it in after creation.

## Checklist

- [x] I have read `PRD.docx`.
- [x] I have completed `DESIGN.md`.
- [x] I have completed `TEST_PLAN.md`.
- [x] I have completed `MOCK_TEST_REPORT.md`.
- [x] I have completed `AI_LOG.md`.
- [x] The project supports the required command:

```bash
python main.py --input Test.txt --output results/received.txt --snr 12 --seed 2026 --mod qpsk --channel awgn
```

- [x] The project generates `results/received.txt`.
- [x] The project generates `results/metrics.json`.
- [x] The project generates at least two required plots.
- [x] I understand the communication principles and code logic of my submission.

## Notes

This project implements the required end-to-end wireless baseband simulation chain. The source codec converts UTF-8 text to bits and restores it after reception. The transmitter uses PN-sequence XOR scrambling, a 3-times repetition channel code, a frame with preamble, length fields, payload, and CRC32 checksum, and Gray-coded unit-power QPSK modulation. The channel model is AWGN with configurable SNR and fixed random seed. The receiver performs preamble-correlation synchronization, QPSK demodulation, frame parsing, channel decoding, descrambling, source decoding, and output comparison.

The project generates `results/received.txt`, `results/metrics.json`, and three plots: QPSK constellation, BER-SNR curve, and synchronization peak. AI was used to assist requirement analysis, design drafting, module implementation, and test-driven debugging; the adopted design and debugging process are recorded in `AI_LOG.md`.
