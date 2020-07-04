from app.models.room import Room


def test_create_room():
    room = Room(1, False, True, 0)

    assert room.room_id == 1
    assert room.is_on == False
    assert room.is_veg_room == True
    assert room.brightness == 0


def test_create_room_from_json():
    room = Room.from_json({"room_id": 1})

    assert room.room_id == 1
    assert room.is_on == False  # auto-initialized to False if not present
    assert room.is_veg_room == False  # auto-initialized to False if not present
    assert room.brightness == None  # auto-initialized to None


def test_to_json():
    room = Room(1, False, True, 0)
    assert room.to_json() == {
        "room_id": 1,
        "is_on": False,
        "is_veg_room": room.is_veg_room,
        "brightness": room.brightness,
    }


def test__str__():
    room = Room(1, False, True, 0)
    assert room.__str__() == str(room)


def test__hash__():
    room = Room(1, False, True, 0)
    assert room.__hash__() == hash(room)


def test__hash__fail():
    room = Room(1, False, True, 0)
    room2 = Room(2, True, True, 0)
    assert not room.__hash__() == room2.__hash__()


def test__eq__():
    room = Room(1, False, True, 0)
    room2 = Room(1, False, True, 0)
    assert room.__eq__(room2)


def test__eq__fail():
    room = Room(1, False, True, 0)
    room2 = Room(4, True, True, 0)
    assert not room.__eq__(room2)
