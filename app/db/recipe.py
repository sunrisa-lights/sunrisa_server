from app.models.recipe import Recipe


def write_recipe(conn, recipe: Recipe):
    recipe_id = recipe.recipe_id
    recipe_name = recipe.recipe_name
    power_level = recipe.power_level
    red_level = recipe.red_level
    blue_level = recipe.blue_level
    num_hours = recipe.num_hours

    sql = "INSERT INTO `recipes` VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE recipe_name=%s, power_level=%s, red_level=%s, blue_level=%s, num_hours=%s"
    conn.cursor().execute(
        sql,
        (
            recipe_id,
            recipe_name,
            power_level,
            red_level,
            blue_level,
            num_hours,
            recipe_name,
            power_level,
            red_level,
            blue_level,
            num_hours,
        ),
    )
    print("WROTE RECIPE", recipe)


def create_recipe_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS recipes(
    recipe_id INT NOT NULL,
    recipe_name VARCHAR(256) NOT NULL,
    power_level INT NOT NULL,
    red_level INT NOT NULL,
    blue_level INT NOT NULL,
    num_hours INT NOT NULL,
    PRIMARY KEY (recipe_id)
    );
    """
    conn.cursor().execute(sql)
