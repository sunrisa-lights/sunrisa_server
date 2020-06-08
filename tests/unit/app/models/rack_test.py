from app.models.rack import Rack


def test_create_rack():
    rack = Rack(1, 2, 40, False, False)

    assert rack.rack_id == 1
    assert rack.room_id == 2
    assert rack.voltage == 40
    assert rack.is_on == False
    assert rack.is_connected == False


def test_create_rack_from_json():
    rack = Rack.from_json({"rack_id": 1, "room_id": 2})

    assert rack.rack_id == 1
    assert rack.room_id == 2
    assert rack.voltage == None  # auto-initialized to None
    assert rack.is_on == None  # auto-initialized to None
    assert rack.is_connected == None  # auto-initialized to None
