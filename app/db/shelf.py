from typing import List, Tuple
from app.models.shelf import Shelf


def write_shelf(conn, shelf: Shelf):
    shelf_id = shelf.shelf_id
    rack_id = shelf.rack_id

    set_values = (shelf_id, rack_id, rack_id)

    sql = "INSERT INTO `shelves` VALUES (%s, %s) ON DUPLICATE KEY UPDATE rack_id=%s"
    cursor = conn.cursor()
    cursor.execute(sql, set_values)
    cursor.close()

    print("WROTE SHELF", shelf)


def read_all_shelves(conn) -> List[Shelf]:
    sql = "SELECT shelf_id, rack_id FROM shelves"
    with conn.cursor() as cursor:
        cursor.execute(sql)
        all_shelves = cursor.fetchall()
        shelves = [Shelf(shelf_id, rack_id) for (shelf_id, rack_id) in all_shelves]
        cursor.close()
        return shelves


def read_shelves_in_rack(conn, rack_id: int) -> List[Shelf]:
    sql = "SELECT shelf_id, rack_id FROM shelves WHERE rack_id=%s"
    with conn.cursor() as cursor:
        cursor.execute(sql, (rack_id))
        all_shelves = cursor.fetchall()
        shelves = [Shelf(shelf_id, rack_id) for (shelf_id, rack_id) in all_shelves]
        cursor.close()
        return shelves


def create_shelf_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS shelves(
    shelf_id INT NOT NULL,
    rack_id INT NOT NULL,
    PRIMARY KEY (shelf_id, rack_id),
    CONSTRAINT fk_rack
    FOREIGN KEY (rack_id)
        REFERENCES racks(rack_id)
    );
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
