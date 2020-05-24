from typing import List

from app.models.rack import Rack


def write_rack(conn, rack: Rack) -> None:
    rack_id = rack.rack_id
    room_id = rack.room_id
    voltage = rack.voltage
    is_on = rack.is_on
    is_connected = rack.is_connected
    print("is_connected:", is_connected)

    set_values = (rack_id, room_id, voltage, is_on, is_connected)

    update_strings = ["room_id=%s"]
    update_values = (room_id,)

    if voltage is not None:
        update_strings.append("voltage=%s")
        update_values += (voltage,)

    if is_on is not None:
        update_strings.append("is_on=%s")
        update_values += (is_on,)

    if is_connected is not None:
        update_strings.append("is_connected=%s")
        update_values += (is_connected,)

    sql = "INSERT INTO `racks` VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE {}".format(', '.join(update_strings))
    conn.cursor().execute(sql, set_values + update_values)

    print("WROTE RACK", rack)

def read_racks_in_room(conn, room_id: int) -> List[Rack]:
    sql = "SELECT rack_id, room_id, voltage, is_on, is_connected FROM racks WHERE room_id=%s"
    with conn.cursor() as cursor:
        cursor.execute(sql, (room_id))
        all_racks = cursor.fetchall()
        racks = [Rack(rack_id, room_id, voltage, bool(is_on), bool(is_connected)) for (rack_id, room_id, voltage, is_on, is_connected) in all_racks]
        return racks


def create_rack_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS racks(
    rack_id INT NOT NULL,
    room_id INT NOT NULL,
    voltage INT,
    is_on BOOLEAN,
    is_connected BOOLEAN,
    PRIMARY KEY (rack_id),
    CONSTRAINT fk_room
    FOREIGN KEY (room_id)
        REFERENCES rooms(room_id)

    );
    """
    conn.cursor().execute(sql)
