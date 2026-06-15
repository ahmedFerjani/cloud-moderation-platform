import hashlib

from _orchestrator_test_setup import orchestrator_services

identity_service = orchestrator_services.identity_service


# Verifies image IDs are derived from S3 object keys consistently.
def test_extract_image_id_from_s3_key() -> None:
    result = identity_service.extract_image_id_from_s3_key("uploads/sample-image.jpg")

    assert result == "sample-image"


# Verifies hash generation is deterministic for a given byte payload.
def test_generate_image_hash_is_deterministic() -> None:
    data = b"abc"
    expected = hashlib.sha256(data).hexdigest()

    assert identity_service.generate_image_hash(data) == expected
