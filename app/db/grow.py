from datetime import datetime
from typing import Any, Dict, List

from app.models.grow import Grow


def write_grow(
    conn,
    grow: Grow
) -> None:
    sql = "INSERT INTO `grows` VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(
        sql, (grow.room_id, grow.rack_id, grow.shelf_id, grow.recipe_id, grow.recipe_phase_num, grow.start_datetime, grow.end_datetime)
    )
    cursor.close()

def read_current_grows(conn) -> List[Grow]:
    sql = "SELECT room_id, rack_id, shelf_id, recipe_id, recipe_phase_num, start_datetime, end_datetime FROM grows WHERE end_time > %s"

    utc_now = datetime.utcnow()
    with conn.cursor() as cursor:
        cursor.execute(sql, (utc_now))
        all_grows = cursor.fetchall()
        print("all_grows", all_grows)
        found_grows: List[Grow] = [
            Grow(room_id, rack_id, sid, rid, rpn, sd, ed)
            for (room_id, rack_id, sid, rid, rpn, sd, ed) in all_grows
        ]

        cursor.close()
        return found_grows

def read_shelf_current_grows(conn, shelf_id) -> List[Grow]:
    sql = "SELECT room_id, rack_id, shelf_id, recipe_id, recipe_phase_num, start_datetime, end_datetime FROM grows WHERE shelf_id=%s AND end_time > %s"

    utc_now = datetime.utcnow()
    with conn.cursor() as cursor:
        cursor.execute(sql, (shelf_id, utc_now))
        all_grows = cursor.fetchall()
        print("all_grows", all_grows)
        found_shelf_grows: List[Grow] = [
            Grow(sid, rid, rpn, sd, ed)
            for (sid, rid, rpn, sd, ed) in all_grows
        ]

        cursor.close()
        return found_shelf_grows


def create_grow_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS grows(
    room_id INT NOT NULL,
    rack_id INT NOT NULL,
    shelf_id INT NOT NULL,
    recipe_id INT NOT NULL,
    recipe_phase_num INT NOT NULL,
    start_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (shelf_id, start_datetime),
    FOREIGN KEY (shelf_id)
        REFERENCES shelves(shelf_id),
    FOREIGN KEY (recipe_id, recipe_phase_num)
        REFERENCES recipe_phases(recipe_id, recipe_phase_num)
    );
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
