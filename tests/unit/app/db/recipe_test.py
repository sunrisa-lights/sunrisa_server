from unittest.mock import MagicMock
import pytest

from app.models.recipe import Recipe
from app.db.recipe import create_recipe_table, write_recipe





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
