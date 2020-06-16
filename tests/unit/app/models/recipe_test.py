from app.models.recipe import Recipe


def test_create_recipe():
    recipe = Recipe(1, "Bamboo")

    assert recipe.recipe_id == 1
    assert recipe.recipe_name == "Bamboo"

def test_create_recipe_from_json():
    recipe = Recipe.from_json(
        {
            "recipe_id": 1,
            "recipe_name": "purp",
        }
    )

    assert recipe.recipe_id == 1
    assert recipe.recipe_name == "purp"
