from app.models.shelf import Shelf


def test_create_shelf():
    shelf = Shelf(1, 2, 3, 4, 5, 6)

    assert shelf.shelf_id == 1
    assert shelf.rack_id == 2
    assert shelf.recipe_id == 3
    assert shelf.power_level == 4
    assert shelf.red_level == 5
    assert shelf.blue_level == 6


def test_create_shelf_from_json():
    shelf = Shelf.from_json({"shelf_id": 1, "rack_id": 2})

    assert shelf.shelf_id == 1
    assert shelf.rack_id == 2
    assert shelf.recipe_id == None
    assert shelf.power_level == None
    assert shelf.red_level == None
    assert shelf.blue_level == None
