from unittest.mock import patch

from _connect_test_setup import connect_services


# Verifies save_connection stores connection metadata with a 24-hour TTL
def test_save_connection_persists_record_with_ttl() -> None:
    with (
        patch.object(connect_services.time, "time", return_value=1_000),
        patch.object(connect_services.table, "put_item") as mock_put,
        patch.object(connect_services, "log") as mock_log,
    ):
        connect_services.save_connection("conn-1", "user-1")

    mock_put.assert_called_once_with(
        Item={
            "connectionId": "conn-1",
            "userId": "user-1",
            "expiresAt": 1_000 + connect_services.CONNECTION_TTL_SECONDS,
        }
    )
    mock_log.assert_called_once()
