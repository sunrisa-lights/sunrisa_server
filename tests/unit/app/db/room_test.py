from unittest.mock import MagicMock
import pytest

from app.models.room import Room
from app.db.room import create_room_table, write_room


@pytest.fixture
def mock_room():
    return Room.from_json(
        {"room_id": 1, "is_on": False, "is_veg_room": True, "brightness": 0}
    )


def test_write_room(mock_room):
    conn = MagicMock()

    write_room(conn, mock_room)

    conn.cursor().execute.assert_called_with(
        "INSERT INTO `rooms` VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE room_id=%s, is_on=%s, is_veg_room=%s, brightness=%s",
        (
            mock_room.room_id,
            mock_room.is_on,
            mock_room.is_veg_room,
            mock_room.brightness,
            mock_room.room_id,
            mock_room.is_on,
            mock_room.is_veg_room,
            mock_room.brightness,
        ),
    )


def test_create_room_table():
    conn = MagicMock()

    create_room_table(conn)
    sql = """CREATE TABLE IF NOT EXISTS rooms(
    room_id INT NOT NULL,
    is_on BOOLEAN,
    is_veg_room BOOLEAN NOT NULL,
    brightness INT,
    PRIMARY KEY (room_id)
    );
    """

    conn.cursor().execute.assert_called_with(sql)
