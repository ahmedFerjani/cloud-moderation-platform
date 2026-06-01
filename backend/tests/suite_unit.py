import sys
import unittest
from pathlib import Path

TESTS_ROOT = Path(__file__).resolve().parent

if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))

TEST_DIRS = (
    TESTS_ROOT / "events",
    TESTS_ROOT / "lambdas" / "content-moderation-api",
    TESTS_ROOT / "lambdas" / "content-moderation-orchestrator",
    TESTS_ROOT / "lambdas" / "content-moderation-dlq-handler",
)


def load_tests(loader, _standard_tests, _pattern):
    suite = unittest.TestSuite()
    for test_dir in TEST_DIRS:
        suite.addTests(
            loader.discover(
                start_dir=str(test_dir),
                pattern="test_*.py",
                top_level_dir=str(test_dir),
            )
        )
    return suite


if __name__ == "__main__":
    unittest.main(buffer=True)
