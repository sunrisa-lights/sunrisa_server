from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.models.grow_phase import GrowPhase


def write_grow_phase(conn, grow_phase: GrowPhase) -> None:
    sql = "INSERT INTO `grow_phases` VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(
        sql,
        (
            grow_phase.grow_id,
            grow_phase.recipe_id,
            grow_phase.recipe_phase_num,
            grow_phase.phase_start_datetime,
            grow_phase.phase_end_datetime,
            grow_phase.is_last_phase,
        ),
    )
    cursor.close()


def write_grow_phases(conn, grow_phases: List[GrowPhase]) -> None:
    grow_phase_sql_args: Tuple[int, ...] = ()
    value_list: List[str] = []
    for g in grow_phases:
        grow_phase_sql_args += (
            g.grow_id,
            g.recipe_id,
            g.recipe_phase_num,
            g.phase_start_datetime,
            g.phase_end_datetime,
            g.is_last_phase,
        )
        value_list.append("(%s, %s, %s, %s, %s, %s)")

    sql = "INSERT INTO `grow_phases` VALUES {}".format(", ".join(value_list))
    cursor = conn.cursor()
    cursor.execute(sql, grow_phase_sql_args)
    cursor.close()


def read_grow_phase(conn, grow_id: int, recipe_phase_num: int) -> Optional[GrowPhase]:
    sql = "SELECT grow_id, recipe_id, recipe_phase_num, start_datetime, end_datetime, is_last_phase FROM grow_phases WHERE grow_id = %s AND recipe_phase_num = %s"

    with conn.cursor() as cursor:
        cursor.execute(sql, (grow_id, recipe_phase_num))
        next_grow_phase = cursor.fetchone()
        found_grow_phase: Optional[GrowPhase] = None
        if found_grow_phase is not None:
            (
                grow_id,
                recipe_id,
                recipe_phase_num,
                start_datetime,
                end_datetime,
                is_last_phase,
            ) = next_grow_phase
            found_grow_phase = GrowPhase(
                grow_id,
                recipe_id,
                recipe_phase_num,
                start_datetime,
                end_datetime,
                is_last_phase,
            )

        cursor.close()
        return found_grow_phase


def read_grow_phases(conn, grow_id: int) -> List[GrowPhase]:
    sql = "SELECT grow_id, recipe_id, recipe_phase_num, start_datetime, end_datetime, is_last_phase FROM grow_phases WHERE grow_id = %s"

    with conn.cursor() as cursor:
        cursor.execute(sql, (grow_id))
        all_grow_phases = cursor.fetchall()
        found_grow_phases: List[GrowPhase] = [
            GrowPhase(grow_id, rid, rpn, sd, ed, ilp)
            for (grow_id, rid, rpn, sd, ed, ilp) in all_grow_phases
        ]

        cursor.close()
        return found_grow_phases


def read_grow_phases_from_multiple_grows(conn, grow_ids: List[int]) -> List[GrowPhase]:
    format_strings = ["%s"] * len(grow_ids)
    sql = "SELECT grow_id, recipe_id, recipe_phase_num, start_datetime, end_datetime, is_last_phase FROM grow_phases WHERE grow_id IN ({})".format(
        ", ".join(format_strings)
    )

    with conn.cursor() as cursor:
        cursor.execute(sql, (grow_ids))
        all_grow_phases = cursor.fetchall()
        found_grow_phases: List[GrowPhase] = [
            GrowPhase(grow_id, rid, rpn, sd, ed, ilp)
            for (grow_id, rid, rpn, sd, ed, ilp) in all_grow_phases
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
    is_last_phase BOOLEAN NOT NULL,
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
