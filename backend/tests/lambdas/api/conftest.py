from collections.abc import Callable

import pytest

from _api_test_setup import api_runtime_event


@pytest.fixture
def api_context():
    return type("Ctx", (), {"aws_request_id": "req-1"})()


@pytest.fixture
def api_event_factory() -> Callable[[str], dict]:
    return api_runtime_event
