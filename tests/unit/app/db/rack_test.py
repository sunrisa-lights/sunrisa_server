from unittest.mock import MagicMock
import pytest

from app.models.rack import Rack
from app.db.rack import create_rack_table, write_rack


@pytest.fixture
def mock_rack():
    return Rack.from_json(
        {"rack_id": 1, "room_id": 2, "is_on": True, "is_connected": True}
    )


def test_write_rack(mock_rack):
    conn = MagicMock()

    write_rack(conn, mock_rack)

    sql = "INSERT INTO `racks` VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE room_id=%s, is_on=%s, is_connected=%s"
    conn.cursor().execute.assert_called_with(
        sql,
        (
            mock_rack.rack_id,
            mock_rack.room_id,
            mock_rack.voltage,
            mock_rack.is_on,
            mock_rack.is_connected,
            mock_rack.room_id,
            mock_rack.is_on,
            mock_rack.is_connected,
        ),
    )


def test_create_rack_table():
    conn = MagicMock()

    create_rack_table(conn)
    sql = """CREATE TABLE IF NOT EXISTS racks(
    rack_id INT NOT NULL,
    room_id INT NOT NULL,
    voltage INT,
    is_on BOOLEAN,
    is_connected BOOLEAN,
    PRIMARY KEY (rack_id),
    CONSTRAINT fk_room
    FOREIGN KEY (room_id)
        REFERENCES rooms(room_id)

    );
    """

    conn.cursor().execute.assert_called_with(sql)
