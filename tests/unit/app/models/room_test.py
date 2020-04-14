from app.models.room import Room

def test_create_room():
    room = Room(1, False, True)

    assert room.roomId == 1
    assert room.isOn == False
    assert room.isVegRoom == True


def test_create_room_from_json():
    room = Room.from_json({'roomId': 1})

    assert room.roomId == 1
    assert room.isOn == False  #auto-initialized to False if not present

