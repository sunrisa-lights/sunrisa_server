from app.models.room import Room

def write_room(conn, room: Room):
    roomId = room.roomId
    isOn = room.isOn
    isVegRoom = room.isVegRoom

    sql = "INSERT INTO `rooms` VALUES (%s, %r, %r) ON DUPLICATE KEY UPDATE is_on=%r, is_veg_room=%r"
    conn.cursor().execute(sql, (roomId, isOn, isVegRoom, isOn, isVegRoom))
    print("WROTE ROOM", room)


def create_room_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS rooms(
    room_id INT NOT NULL,
    is_on BOOLEAN NOT NULL,
    is_veg_room BOOLEAN NOT NULL,
    PRIMARY KEY (room_id)
    );
    """
    conn.cursor().execute(sql)
