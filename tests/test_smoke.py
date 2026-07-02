import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.source import source_decode, source_encode


def test_source_round_trip():
    text = "无线通信 smoke test"
    assert source_decode(source_encode(text)) == text
