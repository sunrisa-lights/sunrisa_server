from app.models.plant import Plant

def write_plant(conn, plant: Plant):
    olcc_number = plant.olcc_number
    shelf_id = plant.shelf_id

    sql = "INSERT INTO `plants` VALUES (%s, %s) ON DUPLICATE KEY UPDATE shelf_id=%s"
    conn.cursor().execute(sql, (olcc_number, shelf_id, shelf_id))
    print("WROTE plant", plant)


def create_plant_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS plants(
    olcc_number INT NOT NULL,
    shelf_id INT,
    PRIMARY KEY (olcc_number),
    CONSTRAINT fk_shelf
    FOREIGN KEY (shelf_id)
        REFERENCES shelves(shelf_id)
    );
    """
    conn.cursor().execute(sql)
