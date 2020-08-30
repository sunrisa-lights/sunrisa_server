from typing import List, Tuple
from app.models.shelf import Shelf


def write_shelf(conn, shelf: Shelf):
    shelf_id = shelf.shelf_id
    rack_id = shelf.rack_id
    room_id = shelf.room_id

    set_values = (shelf_id, room_id, rack_id, room_id, rack_id)

    sql = "INSERT INTO `shelves` VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE room_id=%s, rack_id=%s"
    cursor = conn.cursor()
    cursor.execute(sql, set_values)
    cursor.close()

    print("WROTE SHELF", shelf)


def read_all_shelves(conn) -> List[Shelf]:
    sql = "SELECT shelf_id, room_id, rack_id FROM shelves"
    with conn.cursor() as cursor:
        cursor.execute(sql)
        all_shelves = cursor.fetchall()
        shelves = [
            Shelf(shelf_id, room_id, rack_id)
            for (shelf_id, room_id, rack_id) in all_shelves
        ]
        cursor.close()
        return shelves


def create_shelf_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS shelves(
    shelf_id INT NOT NULL,
    room_id INT NOT NULL,
    rack_id INT NOT NULL,
    PRIMARY KEY (shelf_id, rack_id, room_id),
    CONSTRAINT fk_rack
    FOREIGN KEY (rack_id, room_id)
        REFERENCES racks(rack_id, room_id)
    );
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
