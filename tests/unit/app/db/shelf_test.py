from unittest.mock import MagicMock
import pytest

from app.models.shelf import Shelf
from app.db.shelf import create_shelf_table, write_shelf


@pytest.fixture
def mock_shelf():
    return Shelf.from_json({"shelf_id": 1, "rack_id": 2,})


def test_write_shelf(mock_shelf):
    conn = MagicMock()

    write_shelf(conn, mock_shelf)

    conn.cursor().execute.assert_called_with(
        "INSERT INTO `shelves` VALUES (%s, %s) ON DUPLICATE KEY UPDATE rack_id=%s",
        (mock_shelf.shelf_id, mock_shelf.rack_id, mock_shelf.rack_id,),
    )


def test_create_shelf_table():
    conn = MagicMock()

    create_shelf_table(conn)
    sql = """CREATE TABLE IF NOT EXISTS shelves(
    shelf_id INT NOT NULL,
    rack_id INT NOT NULL,
    PRIMARY KEY (shelf_id, rack_id),
    CONSTRAINT fk_rack
    FOREIGN KEY (rack_id)
        REFERENCES racks(rack_id)
    );
    """

    conn.cursor().execute.assert_called_with(sql)
