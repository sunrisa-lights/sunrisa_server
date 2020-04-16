from unittest.mock import MagicMock
import pytest

from app.models.shelf import Shelf
from app.db.shelf import create_shelf_table, write_shelf


@pytest.fixture
def mock_shelf():
    return Shelf.from_json({'shelf_id': 1, 'rack_id': 2, 'recipe_id': 3})


def test_write_shelf(mock_shelf):
    conn = MagicMock()

    write_shelf(conn, mock_shelf)

    conn.cursor().execute.assert_called_with("INSERT INTO `shelves` VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE recipe_id=%s", (mock_shelf.shelf_id, mock_shelf.rack_id, mock_shelf.recipe_id, mock_shelf.recipe_id))

def test_create_room_table():
    conn = MagicMock()

    create_shelf_table(conn)
    sql = """CREATE TABLE IF NOT EXISTS shelves(
    shelf_id INT NOT NULL,
    rack_id INT NOT NULL,
    recipe_id INT,
    PRIMARY KEY (shelf_id),
    CONSTRAINT fk_rack
    FOREIGN KEY (rack_id)
        REFERENCES racks(rack_id),
    CONSTRAINT fk_recipe
    FOREIGN KEY (recipe_id)
        REFERENCES recipes(recipe_id),

    );
    """

    conn.cursor().execute.assert_called_with(sql)