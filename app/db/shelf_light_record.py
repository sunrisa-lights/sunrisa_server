from datetime import datetime
from typing import Any, Dict, List, Tuple

from app.models.shelf_light_record import ShelfLightRecord


def write_shelf_light_record(
    conn, shelf_light_record: ShelfLightRecord
) -> None:
    sql = "INSERT INTO `shelf_light_records` (room_id, rack_id, shelf_id, red_level, blue_level, power_level, recorded_at) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(
        sql,
        (
            shelf_light_record.room_id,
            shelf_light_record.rack_id,
            shelf_light_record.shelf_id,
            shelf_light_record.red_level,
            shelf_light_record.blue_level,
            shelf_light_record.power_level,
            shelf_light_record.recorded_at,
        ),
    )
    cursor.close()


def write_shelf_light_records(
    conn, shelf_light_records: List[ShelfLightRecord]
) -> None:
    shelf_light_record_sql_args: Tuple[int, ...] = ()
    value_list: List[str] = []
    for shelf_light_record in shelf_light_records:
        shelf_light_record_sql_args += (
            shelf_light_record.room_id,
            shelf_light_record.rack_id,
            shelf_light_record.shelf_id,
            shelf_light_record.red_level,
            shelf_light_record.blue_level,
            shelf_light_record.power_level,
            shelf_light_record.recorded_at,
        )
        value_list.append("(%s, %s, %s, %s, %s, %s, %s)")

    sql = "INSERT INTO `shelf_light_records` (room_id, rack_id, shelf_id, red_level, blue_level, power_level, recorded_at) VALUES {}".format(
        ", ".join(value_list)
    )
    cursor = conn.cursor()
    cursor.execute(sql, shelf_light_record_sql_args)
    cursor.close()


def get_shelf_light_records(
    conn, after_date: datetime
) -> List[ShelfLightRecord]:
    sql = "SELECT room_id, rack_id, shelf_id, red_level, blue_level, power_level, recorded_at from `shelf_light_records` where recorded_at > %s"
    with conn.cursor() as cursor:
        cursor.execute(sql, (after_date))
        light_records = cursor.fetchall()
        found_light_records: List[ShelfLightRecord] = [
            ShelfLightRecord(room, rack, shelf, red, blue, power, recorded_at)
            for (
                room,
                rack,
                shelf,
                red,
                blue,
                power,
                recorded_at,
            ) in light_records
        ]

        cursor.close()
        return found_light_records


def create_shelf_light_record_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS shelf_light_records(
    room_id INT NOT NULL,
    rack_id INT NOT NULL,
    shelf_id INT NOT NULL,
    power_level INT,
    red_level INT,
    blue_level INT,
    recorded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (shelf_id, rack_id, room_id, recorded_at),
    FOREIGN KEY (shelf_id, rack_id, room_id)
        REFERENCES shelves(shelf_id, rack_id, room_id)
    );
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
