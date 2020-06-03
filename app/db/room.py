from typing import List
from typing import Tuple
from typing import Optional

from app.models.room import Room


def write_room(conn, room: Room) -> None:
    room_id = room.room_id
    is_on = room.is_on
    is_veg_room = room.is_veg_room
    brightness = room.brightness

    set_values = (room_id, is_on, is_veg_room, brightness)

    update_strings = ["room_id=%s", "is_on=%s", "is_veg_room=%s"]
    update_values: Tuple[int, ...]  = (room_id, is_on, is_veg_room)

    if brightness is not None:
        update_strings.append("brightness=%s")
        update_values += (brightness,)

    sql = "INSERT INTO `rooms` VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE {}".format(', '.join(update_strings))
    cursor = conn.cursor()
    cursor.execute(sql, set_values + update_values)
    cursor.close()
    print("WROTE ROOM", room)


def read_room(conn, room_id: int) -> Optional[Room]:
    sql = "SELECT room_id, is_on, is_veg_room, brightness FROM rooms WHERE room_id=%s"
    with conn.cursor() as cursor:
        cursor.execute(sql, (room_id))
        found_room_data = cursor.fetchone()
        found_room: Optional[Room] = None
        if found_room_data is not None: # if found_room_data is None, room was not found
            rid, is_on, is_veg, brightness = found_room_data
            found_room = Room(rid, bool(is_on), bool(is_veg), brightness)

        cursor.close()
        return found_room

def read_all_rooms(conn) -> List[Room]:
    sql = "SELECT room_id, is_on, is_veg_room, brightness FROM rooms"
    with conn.cursor() as cursor:
        cursor.execute(sql)
        all_rooms = cursor.fetchall()
        rooms = [Room(rid, bool(is_on), bool(is_veg), brightness) for (rid, is_on, is_veg, brightness) in all_rooms]
<<<<<<< HEAD
        cursor.close()
=======
>>>>>>> master
        return rooms


def create_room_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS rooms(
    room_id INT NOT NULL,
    is_veg_room BOOLEAN NOT NULL,
    is_on BOOLEAN,
    brightness INT,
    PRIMARY KEY (room_id)
    );
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
