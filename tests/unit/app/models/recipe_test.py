from app.models.recipe import Recipe


def test_create_recipe():
    recipe = Recipe(1, "Bamboo")

    assert recipe.recipe_id == 1
    assert recipe.recipe_name == "Bamboo"


def test_create_recipe_from_json():
    recipe = Recipe.from_json({"recipe_id": 1, "recipe_name": "purp"})

    assert recipe.recipe_id == 1
    assert recipe.recipe_name == "purp"


def test_to_json():
    recipe = Recipe(1, "OG Blue Dream")
    assert recipe.to_json() == {
        "recipe_id": 1,
        "recipe_name": recipe.recipe_name,
    }


def test__hash__():
    recipe = Recipe(4, "Gorilla Glue #4")
    recipe2 = Recipe(4, "Gorilla Glue #4")
    assert hash(recipe2) == hash(recipe)


def test__hash__fail():
    recipe = Recipe(4, "Gorilla Glue #4")
    recipe2 = Recipe(1, "OG Blue Dream")
    assert not hash(recipe) == hash(recipe2)


def test__str__():
    recipe = Recipe(4, "Gorilla Glue #4")
    recipe2 = Recipe(4, "Gorilla Glue #4")
    assert str(recipe2) == str(recipe)


def test__eq__():
    recipe = Recipe(4, "Gorilla Glue #4")
    recipe2 = Recipe(4, "Gorilla Glue #4")

    assert recipe == recipe2


def test__eq__fail():
    recipe = Recipe(4, "Gorilla Glue #4")
    recipe2 = Recipe(5, "Gorilla Glue #4")

    assert not recipe == recipe2
