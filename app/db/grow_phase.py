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


def end_grow_phase(conn, grow_phase: GrowPhase, harvest_time: datetime) -> None:
    sql = "UPDATE `grow_phases` SET phase_end_datetime = %s WHERE grow_id = %s AND recipe_phase_num = %s"
    cursor = conn.cursor()
    cursor.execute(sql, (harvest_time, grow_phase.grow_id, grow_phase.recipe_phase_num))
    cursor.close()


# this method is only used for updating grow phases, easiest way to update multiple
# grow phases is with ON DUPLICATE KEY UPDATE
def update_grow_phases(conn, grow_phases: List[GrowPhase]) -> None:
    grow_phase_sql_args: Tuple[int, ...] = ()
    create_value_list: List[str] = []
    for g in grow_phases:
        grow_phase_sql_args += (
            g.grow_id,
            g.recipe_id,
            g.recipe_phase_num,
            g.phase_start_datetime,
            g.phase_end_datetime,
            g.is_last_phase,
        )
        create_value_list.append("(%s, %s, %s, %s, %s, %s)")

    sql = (
        "INSERT INTO `grow_phases` "
        "(grow_id, recipe_id, recipe_phase_num, phase_start_datetime, phase_end_datetime, is_last_phase) "
        "VALUES {} ON DUPLICATE KEY UPDATE "
        "recipe_id=VALUES(recipe_id), recipe_phase_num=VALUES(recipe_phase_num), "
        "phase_start_datetime=VALUES(phase_start_datetime), phase_end_datetime=VALUES(phase_end_datetime), "
        "is_last_phase=VALUES(is_last_phase)"
    )
    sql = sql.format(", ".join(create_value_list))

    print("sql:", sql, "args:", grow_phase_sql_args)
    cursor = conn.cursor()
    cursor.execute(sql, grow_phase_sql_args)
    cursor.close()


def update_grow_phases_recipe_from_grow(conn, grow_id: int, recipe_id: int) -> None:
    sql = "UPDATE `grow_phases` SET recipe_id = %s WHERE grow_id = %s"

    cursor = conn.cursor()
    cursor.execute(sql, (recipe_id, grow_id))
    cursor.close()


def delete_grow_phases_from_grow(conn, grow_id: int) -> None:
    sql = "DELETE FROM `grow_phases` WHERE grow_id = %s"
    cursor = conn.cursor()
    cursor.execute(sql, (grow_id))
    cursor.close()


def read_grow_phase(conn, grow_id: int, recipe_phase_num: int) -> Optional[GrowPhase]:
    sql = "SELECT grow_id, recipe_id, recipe_phase_num, phase_start_datetime, phase_end_datetime, is_last_phase FROM grow_phases WHERE grow_id = %s AND recipe_phase_num = %s"

    with conn.cursor() as cursor:
        cursor.execute(sql, (grow_id, recipe_phase_num))
        next_grow_phase = cursor.fetchone()
        found_grow_phase: Optional[GrowPhase] = None
        if next_grow_phase is not None:
            (
                grow_id,
                recipe_id,
                recipe_phase_num,
                phase_start_datetime,
                phase_end_datetime,
                is_last_phase,
            ) = next_grow_phase
            found_grow_phase = GrowPhase(
                grow_id,
                recipe_id,
                recipe_phase_num,
                phase_start_datetime,
                phase_end_datetime,
                is_last_phase,
            )

        cursor.close()
        return found_grow_phase


def read_grow_phases(conn, grow_id: int) -> List[GrowPhase]:
    sql = "SELECT grow_id, recipe_id, recipe_phase_num, phase_start_datetime, phase_end_datetime, is_last_phase FROM grow_phases WHERE grow_id = %s"

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
    sql = "SELECT grow_id, recipe_id, recipe_phase_num, phase_start_datetime, phase_end_datetime, is_last_phase FROM grow_phases WHERE grow_id IN ({})".format(
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
    phase_start_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    phase_end_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
