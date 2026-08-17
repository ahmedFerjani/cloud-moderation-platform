from unittest.mock import patch

from _disconnect_test_setup import disconnect_services


# Verifies delete_connection removes the connection from DynamoDB by key
def test_delete_connection_removes_record() -> None:
    with (
        patch.object(disconnect_services.table, "delete_item") as mock_delete,
        patch.object(disconnect_services, "log") as mock_log,
    ):
        disconnect_services.delete_connection("conn-1")

    mock_delete.assert_called_once_with(Key={"connectionId": "conn-1"})
    mock_log.assert_called_once()
