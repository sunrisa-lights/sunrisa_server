from app.models.shelf import Shelf

def test_create_shelf():
    shelf = Shelf(1, 2, 3)

    assert shelf.shelf_id == 1
    assert shelf.rack_id == 2
    assert shelf.recipe_id == 3


def test_create_shelf_from_json():
    shelf = Shelf.from_json({'shelf_id': 1, 'rack_id': 2})

    assert shelf.shelf_id == 1
    assert shelf.rack_id == 2
    assert shelf.recipe_id == None

