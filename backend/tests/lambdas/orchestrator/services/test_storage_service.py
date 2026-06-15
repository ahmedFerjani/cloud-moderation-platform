from types import SimpleNamespace
from unittest.mock import patch

from _orchestrator_test_setup import orchestrator_services

storage_service = orchestrator_services.storage_service


# Verifies image download reads bytes from the S3 object body stream.
def test_download_image_reads_s3_body() -> None:
    body = SimpleNamespace(read=lambda: b"img-bytes")
    with patch.object(storage_service.s3, "get_object", return_value={"Body": body}) as mock_get:
        result = storage_service.download_image("bucket", "uploads/a.jpg")

    assert result == b"img-bytes"
    mock_get.assert_called_once_with(
        Bucket="bucket",
        Key="uploads/a.jpg",
        ExpectedBucketOwner=storage_service.EXPECTED_BUCKET_OWNER,
    )


# Verifies uploaded images are deleted from S3 with the expected bucket and key.
def test_delete_uploaded_image_calls_s3_delete() -> None:
    with patch.object(storage_service.s3, "delete_object") as mock_delete:
        storage_service.delete_uploaded_image("bucket", "uploads/a.jpg")

    mock_delete.assert_called_once_with(
        Bucket="bucket",
        Key="uploads/a.jpg",
        ExpectedBucketOwner=storage_service.EXPECTED_BUCKET_OWNER,
    )
