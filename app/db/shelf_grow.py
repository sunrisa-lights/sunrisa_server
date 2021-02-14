from typing import Any, Dict, List, Tuple

from app.models.shelf_grow import ShelfGrow


def write_shelf_grow(conn, shelf_grow: ShelfGrow) -> None:
    sql = "INSERT INTO `shelf_grows` (grow_id, room_id, rack_id, shelf_id) VALUES (%s, %s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(
        sql,
        (
            shelf_grow.grow_id,
            shelf_grow.room_id,
            shelf_grow.rack_id,
            shelf_grow.shelf_id,
        ),
    )
    cursor.close()


def write_shelf_grows(conn, shelf_grows: List[ShelfGrow]) -> None:
    shelf_grow_sql_args: Tuple[int, ...] = ()
    value_list: List[str] = []
    for sg in shelf_grows:
        shelf_grow_sql_args += (sg.grow_id, sg.room_id, sg.rack_id, sg.shelf_id)
        value_list.append("(%s, %s, %s, %s)")

    sql = "INSERT INTO `shelf_grows` (grow_id, room_id, rack_id, shelf_id) VALUES {}".format(
        ", ".join(value_list)
    )
    cursor = conn.cursor()
    cursor.execute(sql, shelf_grow_sql_args)
    cursor.close()


def read_shelves_with_grow(conn, grow_id: int) -> List[ShelfGrow]:
    sql = "SELECT grow_id, room_id, rack_id, shelf_id FROM shelf_grows WHERE grow_id = %s"

    with conn.cursor() as cursor:
        cursor.execute(sql, (grow_id))
        all_shelf_grows = cursor.fetchall()
        print("all_shelf_grows", all_shelf_grows)
        found_shelf_grows: List[ShelfGrow] = [
            ShelfGrow(grow_id, room_id, rack_id, sid)
            for (grow_id, room_id, rack_id, sid) in all_shelf_grows
        ]

        cursor.close()
        return found_shelf_grows


def read_shelves_with_grows(conn, grow_ids: List[int]) -> List[ShelfGrow]:
    grow_ids_str = [str(gid) for gid in grow_ids]
    sql = "SELECT grow_id, room_id, rack_id, shelf_id FROM shelf_grows WHERE grow_id IN ({})".format(
        ", ".join(grow_ids_str)
    )
    with conn.cursor() as cursor:
        cursor.execute(sql)
        all_shelf_grows = cursor.fetchall()
        found_shelf_grows: List[ShelfGrow] = [
            ShelfGrow(grow_id, room_id, rack_id, sid)
            for (grow_id, room_id, rack_id, sid) in all_shelf_grows
        ]

        cursor.close()
        return found_shelf_grows


def create_shelf_grow_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS shelf_grows(
    grow_id INT NOT NULL,
    room_id INT NOT NULL,
    rack_id INT NOT NULL,
    shelf_id INT NOT NULL,
    PRIMARY KEY (grow_id, shelf_id, rack_id, room_id),
    FOREIGN KEY (grow_id)
        REFERENCES grows(grow_id),
    FOREIGN KEY (shelf_id, rack_id, room_id)
        REFERENCES shelves(shelf_id, rack_id, room_id)
    );
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
