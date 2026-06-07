from types import SimpleNamespace
from unittest.mock import patch

import pytest

from _orchestrator_test_setup import orchestrator_validation


# Verifies upload size validation and rejects empty/oversized files.
def test_validate_upload_size_boundaries() -> None:
    with pytest.raises(orchestrator_validation.APPError):
        orchestrator_validation.validate_upload_size(0)

    with pytest.raises(orchestrator_validation.APPError):
        orchestrator_validation.validate_upload_size(6 * 1024 * 1024)

    orchestrator_validation.validate_upload_size(1)


# Verifies non-image payloads raise the invalid-image business error.
def test_validate_image_invalid_file_raises() -> None:
    with patch.object(orchestrator_validation.Image, "open", side_effect=Exception):
        with pytest.raises(orchestrator_validation.APPError) as ctx:
            orchestrator_validation.validate_image(b"not-an-image")

    assert ctx.value.code == "INVALID_IMAGE_FILE"


# Verifies unsupported formats raise the unsupported-image-type business error.
def test_validate_image_unsupported_type_raises() -> None:
    fake_image = SimpleNamespace(format="GIF")
    with patch.object(orchestrator_validation.Image, "open", return_value=fake_image):
        with pytest.raises(orchestrator_validation.APPError) as ctx:
            orchestrator_validation.validate_image(b"gif-bytes")

    assert ctx.value.code == "UNSUPPORTED_IMAGE_TYPE"


# Verifies supported image formats are normalized to lowercase canonical values.
def test_validate_image_supported_type_returns_lowercase() -> None:
    fake_image = SimpleNamespace(format="JPEG")
    with patch.object(orchestrator_validation.Image, "open", return_value=fake_image):
        result = orchestrator_validation.validate_image(b"jpeg-bytes")

    assert result == "jpeg"
