from app.models.shelf import Shelf

def write_shelf(conn, shelf: Shelf):
    shelf_id = shelf.shelf_id
    rack_id = shelf.rack_id
    recipe_id = shelf.recipe_id

    sql = "INSERT INTO `shelves` VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE recipe_id=%s"
    conn.cursor().execute(sql, (shelf_id, rack_id, recipe_id, recipe_id))
    print("WROTE SHELF", shelf)


def create_shelf_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS shelves(
    shelf_id INT NOT NULL,
    rack_id INT NOT NULL,
    recipe_id INT,
    PRIMARY KEY (shelf_id),
    CONSTRAINT fk_rack
    FOREIGN KEY (rack_id)
        REFERENCES racks(rack_id),
    CONSTRAINT fk_recipe
    FOREIGN KEY (recipe_id)
        REFERENCES recipes(recipe_id),

    );
    """
    conn.cursor().execute(sql)
