"""stub_tools.py is a fixed interface; fail loudly if it is ever edited."""
import hashlib
from pathlib import Path

STUB = Path(__file__).resolve().parent.parent / "stub_tools.py"
KIT_SHA256 = "9bbdec877268924a823517b07a43a789f69469c5b213af04b4b29be8873cd409"


def test_stub_is_byte_identical_to_kit():
    assert hashlib.sha256(STUB.read_bytes()).hexdigest() == KIT_SHA256
