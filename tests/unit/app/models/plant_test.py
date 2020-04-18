from app.models.plant import Plant


def test_create_plant():
    plant = Plant(1, 2)

    assert plant.olcc_number == 1
    assert plant.shelf_id == 2


def test_create_plant_from_json():
    plant = Plant.from_json({"olcc_number": 1})

    assert plant.olcc_number == 1
    assert plant.shelf_id == None
