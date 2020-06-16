from unittest.mock import MagicMock
import pytest

from app.models.recipe import Recipe
from app.db.recipe import create_recipe_table, write_recipe


@pytest.fixture
def mock_recipe():
    return Recipe.from_json(
        {
            "recipe_id": 1,
            "recipe_name": "purp",
        }
    )


def test_write_recipe(mock_recipe):
    conn = MagicMock()

    write_recipe(conn, mock_recipe)

    sql = "INSERT INTO `recipes` VALUES (%s, %s) ON DUPLICATE KEY UPDATE recipe_name=%s"
    format_vals = (
        mock_recipe.recipe_id,
        mock_recipe.recipe_name,
        mock_recipe.recipe_name,
    )

    conn.cursor().execute.assert_called_with(sql, format_vals)


def test_create_recipe_table():
    conn = MagicMock()

    create_recipe_table(conn)
    sql = """CREATE TABLE IF NOT EXISTS recipes(
    recipe_id INT NOT NULL AUTO_INCREMENT,
    recipe_name VARCHAR(256),
    PRIMARY KEY (recipe_id)
    );
    """

    conn.cursor().execute.assert_called_with(sql)
