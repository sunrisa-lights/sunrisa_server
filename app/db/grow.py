from datetime import datetime
from typing import Any, Dict, List

from app.models.grow import Grow


def write_grow(
    conn,
    shelf_id: int,
    recipe_id: int,
    recipe_phase_num: int,
    start_datetime: datetime,
    end_datetime: datetime,
) -> None:
    sql = "INSERT INTO `recipe_phases` VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(
        sql, (recipe_id, recipe_phase_num, num_hours, power_level, red_level, blue_level)
    )
    cursor.close()

def read_current_grows(conn) -> List[Grow]:
    sql = "SELECT shelf_id, recipe_id, recipe_phase_num, start_datetime, end_datetime FROM grows WHERE end_time > %s"

    utc_now = datetime.utcnow()
    with conn.cursor() as cursor:
        cursor.execute(sql, (room_id, utc_now))
        all_grows = cursor.fetchall()
        print("all_grows", all_grows)
        found_room_grows: List[Grow] = [
            Grow(sid, rid, rpn, sd, ed)
            for (sid, rid, rpn, sd, ed) in all_grows
        ]

        cursor.close()
        return found_grows


def create_grow_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS grows(
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
