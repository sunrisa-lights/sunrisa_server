from datetime import datetime
from typing import Any, Dict, List

from app.models.recipe_phase import RecipePhase


def write_recipe_phase(
    conn,
    recipe_id: int,
    recipe_phase_num: int,
    num_hours: int,
    power_level: int,
    red_level: int,
    blue_level: int,
) -> None:
    sql = "INSERT INTO `recipe_phases` VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(
        sql, (recipe_id, recipe_phase_num, num_hours, power_level, red_level, blue_level)
    )
    cursor.close()

def create_recipe_phases_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS recipe_phases(
    recipe_id INT NOT NULL,
    recipe_phase_num INT NOT NULL,
    num_hours INT NOT NULL,
    power_level INT NOT NULL,
    red_level INT NOT NULL,
    blue_level INT NOT NULL,
    PRIMARY KEY (recipe_id, recipe_phase_num),
    FOREIGN KEY (recipe_id)
        REFERENCES recipes(recipe_id)
    );
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
