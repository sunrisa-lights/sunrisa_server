from typing import List, Optional

from app.models.recipe import Recipe


def write_recipe(conn, recipe: Recipe) -> Recipe:
    recipe_name = recipe.recipe_name

    sql = "INSERT INTO `recipes` (recipe_name) VALUES (%s)"
    cursor = conn.cursor()
    cursor.execute(sql, (recipe_name))

    # return the id since it's created dynamically on insert by AUTO_INCREMENT
    recipe_id = cursor.lastrowid
    recipe.recipe_id = recipe_id
    cursor.close()

    print("WROTE RECIPE", recipe)
    return recipe


def update_recipe_name(conn, recipe: Recipe) -> None:
    sql = "UPDATE `recipes` SET recipe_name = %s WHERE recipe_id = %s"
    cursor = conn.cursor()
    cursor.execute(sql, (recipe.recipe_name, recipe.recipe_id))

    cursor.close()


def read_recipe(conn, recipe_id: int) -> Optional[Recipe]:
    sql = "SELECT recipe_id, recipe_name FROM recipes WHERE recipe_id = %s"
    with conn.cursor() as cursor:
        cursor.execute(sql, (recipe_id))
        found_recipe = cursor.fetchone()
        recipe: Optional[Recipe] = None
        if found_recipe is not None:
            (recipe_id, recipe_name) = found_recipe
            recipe = Recipe(recipe_id, recipe_name)

        cursor.close()
        return recipe


def read_recipes(conn, recipe_ids: List[int]) -> List[Recipe]:
    recipe_id_str = ",".join([str(rid) for rid in recipe_ids])
    sql = "SELECT recipe_id, recipe_name FROM recipes WHERE recipe_id in ({})".format(
        recipe_id_str
    )
    with conn.cursor() as cursor:
        cursor.execute(sql)
        found_recipes = cursor.fetchall()
        recipes = [Recipe(rid, name) for (rid, name) in found_recipes]
        cursor.close()
        return recipes


def read_recipes_with_name(conn, search_name: str) -> List[Recipe]:
    # have to use .format() because pymysql won't let you escape the %
    sql = "SELECT recipe_id, recipe_name FROM recipes WHERE recipe_name LIKE '%{}%'".format(
        search_name
    )
    with conn.cursor() as cursor:
        cursor.execute(sql)
        found_recipes = cursor.fetchall()
        recipes = [Recipe(rid, name) for (rid, name) in found_recipes]
        cursor.close()
        return recipes


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
