from app.models.recipe import Recipe

def test_create_recipe():
    recipe = Recipe(1, "Bamboo", 40, 49, 50, 100)

    assert recipe.recipe_id == 1
    assert recipe.recipe_name == "Bamboo"
    assert recipe.power_level == 40
    assert recipe.red_level == 49 
    assert recipe.blue_level == 50
    assert recipe.num_hours == 100


def test_create_recipe_from_json():
    recipe = Recipe.from_json({'recipe_id': 1, 'recipe_name': 'purp', 'power_level': 1000, 'red_level': 10, 'blue_level': 20, 'num_hours': 20000})

    assert recipe.recipe_id == 1
    assert recipe.recipe_name == "purp"
    assert recipe.power_level == 1000
    assert recipe.red_level == 10
    assert recipe.blue_level == 20
    assert recipe.num_hours == 20000

