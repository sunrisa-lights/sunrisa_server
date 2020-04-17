from app.models.rack import Rack


def write_rack(conn, rack: Rack):
    rack_id = rack.rack_id
    room_id = rack.room_id
    voltage = rack.voltage
    is_on = rack.is_on
    is_connected = rack.is_connected

    sql = "INSERT INTO `racks` VALUES (%s, %s, %s, %r, %r) ON DUPLICATE KEY UPDATE voltage=%s, is_on=%r, is_connected=%r"
    conn.cursor().execute(
        sql,
        (rack_id, room_id, voltage, is_on, is_connected, voltage, is_on, is_connected),
    )
    print("WROTE RACK", rack)


def create_rack_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS racks(
    rack_id INT NOT NULL,
    room_id INT NOT NULL,
    voltage INT NOT NULL,
    is_on BOOLEAN NOT NULL,
    is_connected BOOLEAN NOT NULL,
    PRIMARY KEY (rack_id),
    CONSTRAINT fk_room
    FOREIGN KEY (room_id)
        REFERENCES rooms(room_id)

    );
    """
    conn.cursor().execute(sql)
