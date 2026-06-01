import sys
import unittest
from pathlib import Path

TESTS_ROOT = Path(__file__).resolve().parent

if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))


def load_tests(loader, _standard_tests, _pattern):
    return loader.discover(
        start_dir=str(TESTS_ROOT / "integration"),
        pattern="test_*.py",
        top_level_dir=str(TESTS_ROOT / "integration"),
    )


if __name__ == "__main__":
    unittest.main(buffer=True)
