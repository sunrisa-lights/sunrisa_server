from app.models.room import Room

def write_room(conn, room: Room):
    roomId = room.roomId
    isOn = room.isOn
    isVegRoom = room.isVegRoom

    sql = "REPLACE INTO `rooms` VALUES (%s, %r, %r)"
    conn.cursor().execute(sql, (roomId, isOn, isVegRoom))
    print("WROTE ROOM", room)
    conn.commit()


def create_room_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS rooms(
    room_id INT NOT NULL,
    is_on BOOLEAN NOT NULL,
    is_veg_room BOOLEAN NOT NULL
    );
    """
    conn.cursor().execute(sql)
