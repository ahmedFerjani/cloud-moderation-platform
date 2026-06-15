import sys
from pathlib import Path

SERVICES_TESTS_DIR = Path(__file__).resolve().parent
ORCHESTRATOR_TESTS_DIR = SERVICES_TESTS_DIR.parent

if str(ORCHESTRATOR_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATOR_TESTS_DIR))
