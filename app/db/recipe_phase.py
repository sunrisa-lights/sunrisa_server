from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models.recipe_phase import RecipePhase


def write_recipe_phases(
    conn,
    recipe_phases: List[RecipePhase]
) -> None:
    
    recipe_phase_sql_args = ()
    value_list = []
    for rp in recipe_phases:
        recipe_phase_sql_args += (rp.recipe_id, rp.recipe_phase_num, rp.num_hours, rp.power_level, rp.red_level, rp.blue_level)
        value_list.append("(%s, %s, %s, %s, %s, %s)")

    # TODO (lww515): Handle updates to existing recipe phases
    sql = "INSERT INTO `recipe_phases` VALUES {}".format(', '.join(value_list))
    cursor = conn.cursor()
    cursor.execute(
        sql, recipe_phase_sql_args
    )
    cursor.close()

def read_lights_from_recipe_phase(conn, recipe_id, recipe_phase_num) -> (Optional[int], Optional[int], Optional[int]):
    sql = "SELECT power_level, red_level, blue_level FROM `recipe_phases` WHERE recipe_id=%s AND recipe_phase_num=%s"
    cursor = conn.cursor()
    with conn.cursor() as cursor:
        cursor.execute(
            sql, (recipe_id, recipe_phase_num)
        )
        light_data = cursor.fetchone()
        cursor.close()
        if (
            light_data is not None
        ):  # if light_data is None, room was not found
            power_level, red_level, blue_level = light_data
            return power_level, red_level, blue_level

        return None, None, None


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
