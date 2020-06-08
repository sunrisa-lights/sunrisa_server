from unittest.mock import MagicMock
import pytest

from app.models.shelf import Shelf
from app.db.shelf import create_shelf_table, write_shelf


@pytest.fixture
def mock_shelf():
    return Shelf.from_json(
        {
            "shelf_id": 1,
            "rack_id": 2,
            "recipe_id": 3,
            "power_level": 4,
            "red_level": 5,
            "blue_level": 6,
        }
    )


def test_write_shelf(mock_shelf):
    conn = MagicMock()

    write_shelf(conn, mock_shelf)

    conn.cursor().execute.assert_called_with(
        "INSERT INTO `shelves` VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE rack_id=%s, recipe_id=%s, power_level=%s, red_level=%s, blue_level=%s",
        (
            mock_shelf.shelf_id,
            mock_shelf.rack_id,
            mock_shelf.recipe_id,
            mock_shelf.power_level,
            mock_shelf.red_level,
            mock_shelf.blue_level,
            mock_shelf.rack_id,
            mock_shelf.recipe_id,
            mock_shelf.power_level,
            mock_shelf.red_level,
            mock_shelf.blue_level,
        ),
    )


def test_create_shelf_table():
    conn = MagicMock()

    create_shelf_table(conn)
    sql = """CREATE TABLE IF NOT EXISTS shelves(
    shelf_id INT NOT NULL,
    rack_id INT NOT NULL,
    recipe_id INT,
    power_level INT,
    red_level INT,
    blue_level INT,
    PRIMARY KEY (shelf_id),
    CONSTRAINT fk_rack
    FOREIGN KEY (rack_id)
        REFERENCES racks(rack_id),
    CONSTRAINT fk_recipe
    FOREIGN KEY (recipe_id)
        REFERENCES recipes(recipe_id)
    );
    """

    conn.cursor().execute.assert_called_with(sql)
