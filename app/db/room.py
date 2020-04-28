from app.models.room import Room


def write_room(conn, room: Room) -> None:
    room_id = room.room_id
    is_on = room.is_on
    is_veg_room = room.is_veg_room

    sql = "INSERT INTO `rooms` VALUES (%s, %r, %r) ON DUPLICATE KEY UPDATE is_on=%r, is_veg_room=%r"
    conn.cursor().execute(sql, (room_id, is_on, is_veg_room, is_on, is_veg_room))
    print("WROTE ROOM", room)


def read_room(conn, room_id: int) -> Room:
    sql = "SELECT room_id, is_on, is_veg_room FROM rooms WHERE room_id=%s"
    with conn.cursor() as cursor:
        cursor.execute(sql, (room_id))
        rid, is_on, is_veg = cursor.fetchone()
        found_room = Room(rid, bool(is_on), bool(is_veg))
        return found_room


def create_room_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS rooms(
    room_id INT NOT NULL,
    is_on BOOLEAN NOT NULL,
    is_veg_room BOOLEAN NOT NULL,
    PRIMARY KEY (room_id)
    );
    """
    conn.cursor().execute(sql)
