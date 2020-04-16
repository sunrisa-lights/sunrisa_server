from unittest.mock import MagicMock
import pytest

from app.models.recipe import Recipe
from app.db.recipe import create_recipe_table, write_recipe


@pytest.fixture
def mock_recipe():
    return Recipe.from_json({'recipe_id': 1, 'recipe_name': 'purp', 'power_level': 1000, 'red_level': 10, 'blue_level': 20, 'num_hours': 20000})


def test_write_recipe(mock_recipe):
    conn = MagicMock()

    write_recipe(conn, mock_recipe)

    sql = "INSERT INTO `recipes` VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE recipe_name=%s, power_level=%s, red_level=%s, blue_level=%s, num_hours=%s"
    format_vals = (mock_recipe.recipe_id, mock_recipe.recipe_name, mock_recipe.power_level, mock_recipe.red_level, mock_recipe.blue_level, mock_recipe.num_hours, mock_recipe.recipe_name, mock_recipe.power_level, mock_recipe.red_level, mock_recipe.blue_level, mock_recipe.num_hours)

    conn.cursor().execute.assert_called_with(sql, format_vals)

def test_create_recipe_table():
    conn = MagicMock()

    create_recipe_table(conn)
    sql = """CREATE TABLE IF NOT EXISTS recipes(
    recipe_id INT NOT NULL,
    recipe_name VARCHAR(256) NOT NULL,
    power_level INT NOT NULL,
    red_level INT NOT NULL,
    blue_level INT NOT NULL,
    num_hours INT NOT NULL,
    PRIMARY KEY (recipe_id)
    );
    """

    conn.cursor().execute.assert_called_with(sql)
