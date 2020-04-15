from app.models.rack import Rack

def test_create_room():
    rack = Rack(1, 2, 40, False, False)

    assert rack.rack_id == 1
    assert rack.room_id == 2
    assert rack.voltage == 40
    assert rack.is_on == False
    assert rack.is_connected == False


def test_create_room_from_json():
    rack = Rack.from_json({'rack_id': 1, 'room_id': 2})

    assert rack.rack_id == 1
    assert rack.room_id == 2
    assert rack.voltage == 0 # auto-initialized to False if not present
    assert rack.is_on == False  # auto-initialized to False if not present
    assert rack.is_connected == False # auto-initialized to False if not present

