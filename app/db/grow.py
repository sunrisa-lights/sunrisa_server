from datetime import datetime
from typing import Any, Dict, List, Tuple

from app.models.grow import Grow


def write_grow(conn, grow: Grow) -> Grow:
    sql = "INSERT INTO `grows` (recipe_id, start_datetime, end_datetime) VALUES (%s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(
        sql,
        (
            grow.recipe_id,
            grow.start_datetime,
            grow.end_datetime,
        ),
    )
    # get id since it's created dynamically on insert by AUTO_INCREMENT
    grow_id = cursor.lastrowid
    grow.grow_id = grow_id
    cursor.close()

    return grow


def write_grows(conn, grows: List[Grow]) -> None:
    grow_sql_args: Tuple[int, ...] = ()
    value_list: List[str] = []
    for g in grows:
        grow_sql_args += (
            g.recipe_id,
            g.start_datetime,
            g.end_datetime,
        )
        value_list.append("(%s, %s, %s)")

    sql = "INSERT INTO `grows` (recipe_id, start_datetime, end_datetime) VALUES {}".format(", ".join(value_list))
    cursor = conn.cursor()
    cursor.execute(sql, grow_sql_args)
    cursor.close()


def read_current_grows(conn) -> List[Grow]:
    sql = "SELECT grow_id, recipe_id, start_datetime, end_datetime FROM grows WHERE end_datetime > %s"

    utc_now = datetime.utcnow()
    with conn.cursor() as cursor:
        cursor.execute(sql, (utc_now))
        all_grows = cursor.fetchall()
        print("all_grows", all_grows)
        found_grows: List[Grow] = [
            Grow(grow_id, room_id, rack_id, sid, rid, sd, ed)
            for (grow_id, room_id, rack_id, sid, rid, sd, ed) in all_grows
        ]

        cursor.close()
        return found_grows


def create_grow_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS grows(
    grow_id INT NOT NULL AUTO_INCREMENT,
    recipe_id INT NOT NULL,
    start_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (grow_id),
    FOREIGN KEY (recipe_id)
        REFERENCES recipes(recipe_id)
    );
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
