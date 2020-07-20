from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.models.recipe_phase import RecipePhase


def write_recipe_phases(conn, recipe_phases: List[RecipePhase]) -> None:
    recipe_phase_sql_args: Tuple[int, ...] = ()
    value_list: List[str] = []
    for rp in recipe_phases:
        recipe_phase_sql_args += (
            rp.recipe_id,
            rp.recipe_phase_num,
            rp.num_hours,
            rp.power_level,
            rp.red_level,
            rp.blue_level,
        )
        value_list.append("(%s, %s, %s, %s, %s, %s)")

    # TODO (lww515): Handle updates to existing recipe phases
    sql = "INSERT INTO `recipe_phases` VALUES {}".format(", ".join(value_list))
    cursor = conn.cursor()
    cursor.execute(sql, recipe_phase_sql_args)
    cursor.close()


def read_lights_from_recipe_phase(
    conn, recipe_id, recipe_phase_num
) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    sql = "SELECT power_level, red_level, blue_level FROM `recipe_phases` WHERE recipe_id=%s AND recipe_phase_num=%s"
    cursor = conn.cursor()
    with conn.cursor() as cursor:
        cursor.execute(sql, (recipe_id, recipe_phase_num))
        light_data = cursor.fetchone()
        cursor.close()
        if light_data is not None:  # if light_data is None, room was not found
            power_level, red_level, blue_level = light_data
            return power_level, red_level, blue_level

        return None, None, None


def read_recipe_phases(
    conn, recipe_id_phase_num_pairs: List[Tuple[int, int]]
) -> List[RecipePhase]:
    values_list: List[str] = []
    for recipe_id, recipe_phase_num in recipe_id_phase_num_pairs:
        values_list.append("({},{})".format(recipe_id, recipe_phase_num))

    sql = "SELECT recipe_id, recipe_phase_num, num_hours, power_level, red_level, blue_level FROM recipe_phases WHERE (recipe_id, recipe_phase_num) IN ({})".format(
        ",".join(values_list)
    )

    with conn.cursor() as cursor:
        cursor.execute(sql)
        found_recipe_phases = cursor.fetchall()
        recipe_phases = [
            RecipePhase(rid, rpn, nh, pl, rl, bl)
            for (rid, rpn, nh, pl, rl, bl) in found_recipe_phases
        ]
        cursor.close()
        return recipe_phases


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
