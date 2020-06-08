from datetime import datetime
from typing import Any, Dict, List

from app.models.schedule import Schedule


def write_schedule_for_shelf(
    conn,
    shelf_id: int,
    start_time: str,
    end_time: str,
    power_level: int,
    red_level: int,
    blue_level: int,
) -> None:
    sql = "INSERT INTO `shelf_schedules` VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(
        sql, (shelf_id, start_time, end_time, power_level, red_level, blue_level)
    )
    cursor.close()


def write_schedule_for_room(
    conn,
    room_id: int,
    start_time: str,
    end_time: str,
    power_level: int,
    red_level: int,
    blue_level: int,
) -> None:
    sql = "INSERT INTO `room_schedules` VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(
        sql, (room_id, start_time, end_time, power_level, red_level, blue_level)
    )
    cursor.close()


def read_current_room_schedules(conn, room_id: int) -> List[Schedule]:
    sql = "SELECT room_id, start_time, end_time, power_level, red_level, blue_level FROM room_schedules WHERE room_id=%s AND end_time > %s"

    utc_now = datetime.utcnow()
    with conn.cursor() as cursor:
        cursor.execute(sql, (room_id, utc_now))
        all_room_schedules = cursor.fetchall()
        print("all_room_schedules", all_room_schedules)
        found_room_schedules: List[Schedule] = [
            Schedule(rid, None, sdt, edt, pl, rl, bl)
            for (rid, sdt, edt, pl, rl, bl) in all_room_schedules
        ]

        cursor.close()
        return found_room_schedules


def create_shelf_schedule_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS shelf_schedules(
    shelf_id INT,
    start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    power_level INT NOT NULL,
    red_level INT NOT NULL,
    blue_level INT NOT NULL,
    PRIMARY KEY (shelf_id, start_time, end_time),
    CONSTRAINT fk_shelf_schedule
    FOREIGN KEY (shelf_id)
        REFERENCES shelves(shelf_id)
    );
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()


def create_room_schedule_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS room_schedules(
    room_id INT,
    start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    power_level INT NOT NULL,
    red_level INT NOT NULL,
    blue_level INT NOT NULL,
    PRIMARY KEY (room_id, start_time, end_time),
    CONSTRAINT fk_room_schedule
    FOREIGN KEY (room_id)
        REFERENCES rooms(room_id)
    );
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
