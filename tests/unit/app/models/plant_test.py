from app.models.plant import Plant


def test_create_plant():
    plant = Plant(1, 2)

    assert plant.olcc_number == 1
    assert plant.shelf_id == 2


def test_create_plant_from_json():
    plant = Plant.from_json({"olcc_number": 1})

    assert plant.olcc_number == 1
    assert plant.shelf_id is None


def test__str__():
    plant = Plant(3, 4)
    assert plant.__str__() == str(plant)


def test__eq__():
    plant = Plant(5, 6)
    plant2 = Plant(5, 6)
    assert plant == plant2


def test__eq__fail():
    plant2 = Plant(7, 8)
    plant3 = Plant(5, 6)
    assert not plant2.__eq__(plant3)
