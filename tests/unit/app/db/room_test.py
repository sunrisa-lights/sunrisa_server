from unittest.mock import MagicMock
import pytest

from app.models.room import Room
from app.db.room import create_room_table, read_room, write_room


@pytest.fixture
def mock_room():
    return Room.from_json({"room_id": 1, "is_on": False, "is_veg_room": True})


def test_write_room(mock_room):
    conn = MagicMock()

    write_room(conn, mock_room)

    conn.cursor().execute.assert_called_with(
        "INSERT INTO `rooms` VALUES (%s, %r, %r) ON DUPLICATE KEY UPDATE is_on=%r, is_veg_room=%r",
        (
            mock_room.room_id,
            mock_room.is_on,
            mock_room.is_veg_room,
            mock_room.is_on,
            mock_room.is_veg_room,
        ),
    )


def test_create_room_table():
    conn = MagicMock()

    create_room_table(conn)
    sql = """CREATE TABLE IF NOT EXISTS rooms(
    room_id INT NOT NULL,
    is_on BOOLEAN NOT NULL,
    is_veg_room BOOLEAN NOT NULL,
    PRIMARY KEY (room_id)
    );
    """

    conn.cursor().execute.assert_called_with(sql)
