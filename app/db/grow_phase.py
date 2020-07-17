from datetime import datetime
from typing import Any, Dict, List, Tuple

from app.models.grow_phase import GrowPhase


def write_grow_phase(conn, grow_phase: GrowPhase) -> None:
    sql = "INSERT INTO `grow_phases` VALUES (%s, %s, %s, %s, %s"
    cursor = conn.cursor()
    cursor.execute(
        sql,
        (
            grow.grow_id,
            grow.recipe_id,
            grow.recipe_phase_num,
            grow.start_datetime,
            grow.end_datetime,
        ),
    )
    cursor.close()


def write_grow_phases(conn, grow_phases: List[GrowPhase]) -> None:
    grow_phase_sql_args: Tuple[int, ...] = ()
    value_list: List[str] = []
    for g in grow_phases:
        grow_sql_args += (
            g.grow_id,
            g.recipe_id,
            g.recipe_phase_num,
            g.start_datetime,
            g.end_datetime,
        )
        value_list.append("(%s, %s, %s, %s, %s)")

    sql = "INSERT INTO `grow_phases` VALUES {}".format(", ".join(value_list))
    cursor = conn.cursor()
    cursor.execute(sql, grow_phase_sql_args)
    cursor.close()


def read_grow_phases(conn, grow_id: int) -> List[GrowPhase]:
    sql = "SELECT grow_id, recipe_id, recipe_phase_num, start_datetime, end_datetime FROM grow_phases WHERE grow_id = %s"

    with conn.cursor() as cursor:
        cursor.execute(sql, (grow_id))
        all_grow_phases = cursor.fetchall()
        found_grow_phases: List[GrowPhase] = [
            GrowPhase(grow_id, rid, rpn, sd, ed)
            for (grow_id, rid, rpn, sd, ed) in all_grow_phases
        ]

        cursor.close()
        return found_grow_phases

def read_grow_phases_from_multiple_grows(conn, grow_ids: List[int]) -> List[GrowPhase]:
    format_strings = ["%s"] * len(grow_ids)
    sql = "SELECT grow_id, recipe_id, recipe_phase_num, start_datetime, end_datetime FROM grow_phases WHERE grow_id = ({})".format(', '.join(format_strings))

    with conn.cursor() as cursor:
        cursor.execute(sql, (grow_ids))
        all_grow_phases = cursor.fetchall()
        found_grow_phases: List[GrowPhase] = [
            GrowPhase(grow_id, rid, rpn, sd, ed)
            for (grow_id, rid, rpn, sd, ed) in all_grow_phases
        ]

        cursor.close()
        return found_grow_phases


def create_grow_phase_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS grow_phases(
    grow_id INT NOT NULL,
    recipe_id INT NOT NULL,
    recipe_phase_num INT NOT NULL,
    start_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (grow_id, recipe_phase_num),
    FOREIGN KEY (grow_id)
        REFERENCES grows(grow_id),
    FOREIGN KEY (recipe_id, recipe_phase_num)
        REFERENCES recipe_phases(recipe_id, recipe_phase_num)
    );
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()