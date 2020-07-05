from app.models.shelf import Shelf


def test_create_shelf():
    shelf = Shelf(1, 2)

    assert shelf.shelf_id == 1
    assert shelf.rack_id == 2


def test_create_shelf_from_json():
    shelf = Shelf.from_json({"shelf_id": 1, "rack_id": 2})

    assert shelf.shelf_id == 1
    assert shelf.rack_id == 2


def test_to_json():
    shelf = Shelf(1, 2)
    assert shelf.to_json() == {
        "shelf_id": 1,
        "rack_id": 2,
    }


def test__str__():
    shelf = Shelf(1, 2)
    shelf2 = Shelf(1, 2)
    assert str(shelf2) == str(shelf)


def test__hash__():
    shelf = Shelf(1, 2)
    shelf2 = Shelf(1, 2)
    assert hash(shelf2) == hash(shelf)


def test__hash__fail():
    shelf = Shelf(1, 2)
    shelf2 = Shelf(12, 6)
    assert not hash(shelf) == hash(shelf2)


def test__eq__():
    shelf = Shelf(1, 2)
    shelf2 = Shelf(1, 2)
    assert shelf == shelf2


def test__eq__fail():
    shelf = Shelf(1, 2)
    shelf2 = Shelf(4, 5)
    assert not shelf == shelf2
