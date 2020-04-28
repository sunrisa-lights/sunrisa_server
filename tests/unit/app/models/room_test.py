from app.models.room import Room


def test_create_room():
    room = Room(1, False, True)

    assert room.room_id == 1
    assert room.is_on == False
    assert room.is_veg_room == True


def test_create_room_from_json():
    room = Room.from_json({"room_id": 1})

    assert room.room_id == 1
    assert room.is_on == False  # auto-initialized to False if not present
