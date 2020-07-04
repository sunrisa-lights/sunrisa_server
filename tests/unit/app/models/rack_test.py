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


def test_to_json():
    rack = Rack(1, 2, 40, None, True)
    assert rack.to_json() == {
        "rack_id": 1,
        "room_id": 2,
        "voltage": 40,
        "is_on": None,
        "is_connected": True,
    }


def test__str__():
    rack = Rack(1, 2, 49, False, None)
    assert rack.__str__() == str(rack)


def test__hash__():
    rack = Rack(1, 3, 50, None, True)
    assert rack.__hash__() == hash(rack)


def test__hash__fail():
    rack = Rack(1, 3, 50, None, True)
    rack2 = Rack(1, 2, 49, False, None)
    assert not rack.__hash__() == rack2.__hash__()


def test__eq__():
    rack = Rack(1, 2, 49, False, None)
    rack2 = Rack(1, 2, 49, False, None)
    assert rack.__eq__(rack2)


def test__eq__fail():
    rack = Rack(1, 2, 49, False, None)
    rack2 = Rack(1, 3, 49, True, False)
    assert not rack.__eq__(rack2)
