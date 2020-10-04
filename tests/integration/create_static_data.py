import socketio
import sys

from typing import List, Tuple

# TODO(lwotton): Remove this hack
sys.path.append(".")

from app.models.room import Room
from app.models.rack import Rack
from app.models.shelf import Shelf


def create_rooms(sio, num_rooms: int) -> List[int]:
    room_ids: List[int] = []
    for i in range(num_rooms):
        room_dict = {
            "room": {
                "room_id": i + 1,
                "is_on": False,
                "is_veg_room": True,
                "brightness": 0,
            }
        }
        sio.emit("message_sent", room_dict)
        sio.sleep(1)
        room_ids.append(i + 1)

    return room_ids


def create_racks(
    sio, num_racks_in_room: int, room_ids: List[int]
) -> List[Tuple[int, int]]:
    rack_ids_room_ids: List[Tuple[int, int]] = []
    for i in range(num_racks_in_room):
        for room_id in room_ids:
            rack_dict = {
                "rack": {
                    "rack_id": i + 1,
                    "room_id": room_id,
                    "voltage": 100,
                    "is_on": True,
                    "is_connected": True,
                }
            }
            sio.emit("message_sent", rack_dict)
            sio.sleep(1)
            rack_ids_room_ids.append((i + 1, room_id))

    return rack_ids_room_ids


def create_shelves(
    sio, num_shelves_in_rack: int, rack_ids_room_ids: List[Tuple[int, int]]
) -> None:
    for i in range(num_shelves_in_rack):
        for rack_id, room_id in rack_ids_room_ids:
            shelf_dict = {
                "shelf": {
                    "shelf_id": i + 1,
                    "rack_id": rack_id,
                    "room_id": room_id,
                }
            }
            sio.emit("message_sent", shelf_dict)
            sio.sleep(1)


def create_static_data(sio):
    num_rooms = 2
    num_racks_in_room = 2
    num_shelves_in_rack = 3
    room_ids: List[int] = create_rooms(sio, num_rooms)
    rack_ids_room_ids: List[Tuple[int, int]] = create_racks(
        sio, num_racks_in_room, room_ids
    )
    create_shelves(sio, num_shelves_in_rack, rack_ids_room_ids)

    print("Static data events emitted")


def run_and_disconnect(test_func):
    sio = socketio.Client()
    sio.connect("http://localhost:5000")
    test_func(sio)
    sio.disconnect()


if __name__ == "__main__":
    run_and_disconnect(create_static_data)
