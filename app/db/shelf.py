from typing import Tuple
from app.models.shelf import Shelf


def write_shelf(conn, shelf: Shelf):
    shelf_id = shelf.shelf_id
    rack_id = shelf.rack_id
    recipe_id = shelf.recipe_id
    power_level = shelf.power_level
    red_level = shelf.red_level
    blue_level = shelf.blue_level

    print("RECIPE_ID:", recipe_id)
    set_values = (shelf_id, rack_id, recipe_id, power_level, red_level, blue_level)

    update_strings = ["rack_id=%s"]
    update_values: Tuple[int, ...] = (rack_id,)

    if recipe_id is not None:
        update_strings.append("recipe_id=%s")
        update_values += (recipe_id,)

    if power_level is not None:
        update_strings.append("power_level=%s")
        update_values += (power_level,)

    if red_level is not None:
        update_strings.append("red_level=%s")
        update_values += (red_level,)

    if blue_level is not None:
        update_strings.append("blue_level=%s")
        update_values += (blue_level,)

    sql = (
        "INSERT INTO `shelves` VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE {}".format(', '.join(update_strings))
    )
    conn.cursor().execute(sql, set_values + update_values)

    print("WROTE SHELF", shelf)


def create_shelf_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS shelves(
    shelf_id INT NOT NULL,
    rack_id INT NOT NULL,
    recipe_id INT,
    power_level INT,
    red_level INT,
    blue_level INT,
    PRIMARY KEY (shelf_id),
    CONSTRAINT fk_rack
    FOREIGN KEY (rack_id)
        REFERENCES racks(rack_id),
    CONSTRAINT fk_recipe
    FOREIGN KEY (recipe_id)
        REFERENCES recipes(recipe_id)
    );
    """
    conn.cursor().execute(sql)
