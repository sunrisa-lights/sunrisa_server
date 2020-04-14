from unittest.mock import MagicMock, patch
import pytest

from app.db.db import DB
from app.models.room import Room


@pytest.fixture
def mock_db():
    conn = MagicMock()
    logger = MagicMock()
    DB_NAME = "db_test"
    db = DB(conn, DB_NAME, logger)
    return db

@pytest.fixture
def mock_room():
    return Room.from_json({'roomId': 1, 'isOn': True, 'isVegRoom': True})


@patch('app.db.db.write_room')
def test_write_room(mock_write_room, mock_db, mock_room):
    mock_write_room.return_value = None
    mock_db.write_room(mock_room)
    mock_write_room.assert_called_with(mock_db.conn, mock_room)
