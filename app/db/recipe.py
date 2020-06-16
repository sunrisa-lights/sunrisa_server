from datetime import datetime
from app.models.recipe import Recipe


def write_recipe(conn, recipe: Recipe):
    recipe_id = recipe.recipe_id
    recipe_name = recipe.recipe_name

    sql = "INSERT INTO `recipes` VALUES (%s, %s) ON DUPLICATE KEY UPDATE recipe_name=%s"
    cursor = conn.cursor()
    cursor.execute(
        sql, (recipe_id, recipe_name, recipe_name,),
    )
    cursor.close()
    print("WROTE RECIPE", recipe)


def create_recipe_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS recipes(
    recipe_id INT NOT NULL AUTO_INCREMENT,
    recipe_name VARCHAR(256),
    PRIMARY KEY (recipe_id)
    );
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
