from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.models.grow import Grow


def write_grow(conn, grow: Grow) -> Grow:
    sql = "INSERT INTO `grows` (recipe_id, start_datetime, estimated_end_datetime, is_finished, all_fields_complete) VALUES (%s, %s, %s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(
        sql, (grow.recipe_id, grow.start_datetime, grow.estimated_end_datetime, grow.is_finished, grow.all_fields_complete),
    )
    # return the id since it's created dynamically on insert by AUTO_INCREMENT
    grow_id = cursor.lastrowid
    grow.grow_id = grow_id
    cursor.close()

    return grow

def harvest_grow(conn, grow: Grow) -> Grow:
    sql = "UPDATE `grows` SET estimated_end_datetime = %s, is_finished = %s, all_fields_complete = %s, olcc_number = %s WHERE grow_id = %s"
    cursor = conn.cursor()
    print("grow to harvest in db layer:", grow)
    cursor.execute(
        sql, (grow.estimated_end_datetime, grow.is_finished, grow.all_fields_complete, grow.olcc_number, grow.grow_id),
    )
    cursor.close()

    return grow

def read_grow(conn, grow_id: int) -> Optional[Grow]:
    sql = "SELECT grow_id, recipe_id, start_datetime, estimated_end_datetime, is_finished, all_fields_complete, olcc_number FROM grows WHERE grow_id = %s"

    with conn.cursor() as cursor:
        cursor.execute(sql, (grow_id))
        found_grow = cursor.fetchone()
        grow: Optional[Grow] = None
        if found_grow is not None:
            (
                grow_id,
                recipe_id,
                start_datetime,
                estimated_end_datetime,
                is_finished,
                all_fields_complete,
                olcc_number,
            ) = found_grow
            grow = Grow(
                grow_id,
                recipe_id,
                start_datetime,
                estimated_end_datetime,
                is_finished,
                all_fields_complete,
                olcc_number,
            )

        cursor.close()
        return grow

def read_current_grows(conn) -> List[Grow]:
    sql = "SELECT grow_id, recipe_id, start_datetime, estimated_end_datetime, is_finished, all_fields_complete, olcc_number FROM grows WHERE is_finished = false"

    with conn.cursor() as cursor:
        cursor.execute(sql)
        all_grows = cursor.fetchall()
        print("all_grows", all_grows)
        found_grows: List[Grow] = [
            Grow(grow_id, rid, sd, ed, fin, comp, olcc) for (grow_id, rid, sd, ed, fin, comp, olcc) in all_grows
        ]

        cursor.close()
        return found_grows


def create_grow_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS grows(
    grow_id INT NOT NULL AUTO_INCREMENT,
    recipe_id INT,
    start_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estimated_end_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_finished BOOLEAN NOT NULL,
    all_fields_complete BOOLEAN NOT NULL,
    olcc_number INT,
    PRIMARY KEY (grow_id),
    FOREIGN KEY (recipe_id)
        REFERENCES recipes(recipe_id)
    );
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
