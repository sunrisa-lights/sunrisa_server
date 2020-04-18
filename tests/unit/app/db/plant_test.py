from unittest.mock import MagicMock
import pytest

from app.models.plant import Plant
from app.db.plant import create_plant_table, write_plant


@pytest.fixture
def mock_plant():
    return Plant.from_json({"olcc_number": 1, "shelf_id": 2})


def test_write_plant(mock_plant):
    conn = MagicMock()

    write_plant(conn, mock_plant)

    sql = "INSERT INTO `plants` VALUES (%s, %s) ON DUPLICATE KEY UPDATE shelf_id=%s"
    conn.cursor().execute.assert_called_with(
        sql, (mock_plant.olcc_number, mock_plant.shelf_id, mock_plant.shelf_id)
    )


def test_create_plant_table():
    conn = MagicMock()

    create_plant_table(conn)
    sql = """CREATE TABLE IF NOT EXISTS plants(
    olcc_number INT NOT NULL,
    shelf_id INT,
    PRIMARY KEY (olcc_number),
    CONSTRAINT fk_shelf
    FOREIGN KEY (shelf_id)
        REFERENCES shelves(shelf_id)
    );
    """

    conn.cursor().execute.assert_called_with(sql)
