from unittest.mock import MagicMock
import pytest

from app.models.rack import Rack
from app.db.rack import create_rack_table, write_rack


@pytest.fixture
def mock_rack():
    return Rack.from_json({'rack_id': 1, 'room_id': 2, 'is_connected': True})


def test_write_rack(mock_rack):
    conn = MagicMock()

    write_rack(conn, mock_rack)

    sql = "INSERT INTO `racks` VALUES (%s, %s, %s, %r, %r) ON DUPLICATE KEY UPDATE voltage=%s, is_on=%r, is_connected=%r"
    conn.cursor().execute.assert_called_with("INSERT INTO `racks` VALUES (%s, %s, %s, %r, %r) ON DUPLICATE KEY UPDATE voltage=%s, is_on=%r, is_connected=%r", (mock_rack.rack_id, mock_rack.room_id, mock_rack.voltage, mock_rack.is_on, mock_rack.is_connected, mock_rack.voltage, mock_rack.is_on, mock_rack.is_connected))

def test_create_rack_table():
    conn = MagicMock()

    create_rack_table(conn)
    sql = """CREATE TABLE IF NOT EXISTS racks(
    rack_id INT NOT NULL,
    room_id INT NOT NULL,
    voltage INT NOT NULL,
    is_on BOOLEAN NOT NULL,
    is_connected BOOLEAN NOT NULL,
    PRIMARY KEY (rack_id),
    CONSTRAINT fk_room
    FOREIGN KEY (room_id)
        REFERENCES rooms(room_id)

    );
    """

    conn.cursor().execute.assert_called_with(sql)
