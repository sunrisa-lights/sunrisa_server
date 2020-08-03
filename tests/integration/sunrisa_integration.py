import collections
import socketio
import pymysql.cursors
import logging
import sys
import time
from datetime import date, datetime, timedelta, timezone

from typing import List

# TODO(lwotton): Remove this hack
sys.path.append(".")

from app.models.grow import Grow
from app.models.grow_phase import GrowPhase
from app.models.room import Room
from app.models.rack import Rack
from app.models.recipe import Recipe
from app.models.recipe_phase import RecipePhase
from app.models.shelf import Shelf

expected_processed_entities = None


def kill_server_on_assert_failure(sio, condition, assert_arg=""):
    if not condition:
        sio.disconnect()

    assert condition, assert_arg


# flag should be an empty list that is populated and has a certain length
def wait_for_event(sio, flag, length_condition, num_seconds, test_name):
    seconds_counter = 0
    while len(flag) != length_condition and seconds_counter < num_seconds:
        time.sleep(1)
        seconds_counter += 1

    if not flag:
        kill_server_on_assert_failure(
            sio, False, "Timed out waiting for event for test {}".format(test_name)
        )


def _test_send_room(sio):
    # send initial room update
    room_dict = {
        "room": {"room_id": 1, "is_on": False, "is_veg_room": True, "brightness": 5}
    }
    sio.emit("message_sent", room_dict)
    sio.sleep(1)

    flag = []

    @sio.on("return_room")
    def find_room_listener(message) -> None:
        print("got message:", message)
        assert "room" in message
        assert message["room"] is not None
        returned_room = Room.from_json(message["room"])
        expected_room = Room.from_json(room_dict["room"])

        print("returned_room:", returned_room, "expected_room:", expected_room)
        assert returned_room == expected_room
        flag.append(True)

    sio.emit("read_room", room_dict)

    wait_for_event(sio, flag, 1, 5, "test_send_room.create_room")

    print("first room found and returned")

    # update same room to on
    room_dict["room"]["is_on"] = not room_dict["room"]["is_on"]
    sio.emit("message_sent", room_dict)

    sio.emit("read_room", room_dict)

    wait_for_event(sio, flag, 2, 5, "test_send_room.update_room")

    print("second room read and updated")

    # create new room
    room_dict2 = {
        "room": {"room_id": 2, "is_on": False, "is_veg_room": True, "brightness": 80},
    }
    sio.emit("message_sent", room_dict2)
    sio.sleep(1)

    # return both rooms
    rooms = []

    @sio.on("return_rooms")
    def find_all_rooms_listener(message) -> None:
        found_rooms = message["rooms"]
        for fr in found_rooms:
            rooms.append(Room.from_json(fr))

        room_map = {room.room_id: room for room in rooms}
        first_id = room_dict["room"]["room_id"]
        second_id = room_dict2["room"]["room_id"]
        assert room_map[first_id] == Room.from_json(room_dict["room"])
        assert room_map[second_id] == Room.from_json(room_dict2["room"])

    sio.emit("read_all_rooms", {})
    wait_for_event(sio, rooms, 2, 5, "test_send_room.read_rooms")
    print("read all rooms")

    return [Room.from_json(room_dict["room"]), Room.from_json(room_dict2["room"])]


def _test_send_rack(sio, room):
    # send initial rack update with created room id
    rack_dict = {
        "rack": {
            "rack_id": 2,
            "room_id": room.room_id,
            "voltage": 100,
            "is_on": True,
            "is_connected": True,
        },
    }
    sio.emit("message_sent", rack_dict)
    sio.sleep(1)

    flag = []

    @sio.on("return_racks_in_room")
    def return_racks_in_room_listener(message) -> None:
        found_racks = message["racks"]
        room_id = message["room_id"]

        print("found_racks:", found_racks, rack_dict)
        assert len(found_racks) == 1
        assert Rack.from_json(found_racks[0]) == Rack.from_json(rack_dict["rack"])
        assert room_id == room.room_id

        flag.append(True)

    sio.emit(
        "read_all_racks_in_room", {"room": {"room_id": room.room_id}},
    )
    wait_for_event(sio, flag, 1, 10, "test_send_rack.read_all_racks_in_room.1")

    print("first rack found and returned")

    # update same rack to on
    rack_dict["rack"]["is_on"] = not rack_dict["rack"]["is_on"]
    sio.emit("message_sent", rack_dict)
    sio.emit(
        "read_all_racks_in_room", {"room": {"room_id": room.room_id}},
    )
    wait_for_event(sio, flag, 2, 10, "test_send_rack.read_all_racks_in_room.2")

    print("second rack found and returned")

    return Rack.from_json(rack_dict["rack"])


def _test_send_shelf(sio, rack):
    shelf_dict = {
        "shelf": {"shelf_id": 1, "rack_id": rack.rack_id,},
    }
    sio.emit("message_sent", shelf_dict)
    sio.sleep(1)
    expected = Shelf.from_json(shelf_dict["shelf"])

    return expected



def _test_send_shelf_grow(sio, room_id, rack_id, shelf_id):
    print("Sending shelf grow")
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    end = start + timedelta(0, 2)  # 5 seconds from now

    start_time = start.strftime("%Y-%m-%d %H:%M:%S")
    end_time = end.strftime("%Y-%m-%d %H:%M:%S")

    shelf_grows = [{
                "room_id": room_id,
                "rack_id": rack_id,
                "shelf_id": shelf_id,
            }]
    recipe_phases = [
            {
                "start_date": start.strftime("%Y-%m-%d %H:%M:%S"),
                "power_level": 9,
                "red_level": 8,
                "blue_level": 7,
            }
        ]

    is_new_recipe = True
    flag = []

    @sio.on("start_grows_for_shelves_succeeded")
    def start_grows_for_shelves_succeeded(message) -> None:
        assert "succeeded" in message
        assert message["succeeded"]
        flag.append(True)

    @sio.on("set_lights_for_grow")
    def set_lights_for_grow(message) -> None:
        assert "grow" in message
        assert "power_level" in message
        assert "red_level" in message
        assert "blue_level" in message
        flag.append(True)
    start_grows_for_shelves_dict = {
        "shelves": shelf_grows, 
        "grow_phases": recipe_phases,
        "is_new_recipe": is_new_recipe,
        "end_date": end_time
    }
    sio.emit("start_grows_for_shelves", start_grows_for_shelves_dict)
    wait_for_event(sio, flag, 1, 10, "test_start_grows_for_shelves")

    print("test send shelf grow passed")
    return(start_time, end_time, recipe_phases)


def _test_find_all_entities(
    sio,
    rooms: List[Room],
    racks: List[Rack],
    shelves: List[Shelf],
    start,
    end,
    p_level,
    r_level,
    b_level

):
    flag = []

    @sio.on("return_all_entities")
    def return_all_entities_listener(message) -> None:
        print("Received message in entities_listener:", message)
        assert "rooms" in message
        assert "racks" in message
        assert "shelves" in message
        assert "grows" in message
        assert "grow_phases" in message
        assert "recipes" in message
        assert "recipe_phases" in message
        found_rooms = [Room.from_json(r) for r in message["rooms"]]
        found_racks = [Rack.from_json(r) for r in message["racks"]]
        found_shelves = [Shelf.from_json(s) for s in message["shelves"]]
        found_grows = [Grow.from_json(g) for g in message["grows"]]
        found_grow_phases = [GrowPhase.from_json(g) for g in message["grow_phases"]]
        found_recipes = [Recipe.from_json(r) for r in message["recipes"]]
        found_recipe_phases = [
            RecipePhase.from_json(rp) for rp in message["recipe_phases"]
        ]

        assert collections.Counter(found_rooms) == collections.Counter(rooms)
        assert collections.Counter(found_racks) == collections.Counter(racks)
        assert collections.Counter(found_shelves) == collections.Counter(shelves)
        if len(found_grows) == 1:
            assert found_grows[0].start_datetime.strftime("%Y-%m-%d %H:%M:%S") == start
            assert found_grows[0].estimated_end_datetime.strftime("%Y-%m-%d %H:%M:%S") == end
        assert found_grow_phases[0].phase_start_datetime.strftime("%Y-%m-%d %H:%M:%S") == start
        assert found_grow_phases[0].phase_end_datetime.strftime("%Y-%m-%d %H:%M:%S") == end
        assert len(found_recipes) == 1 
        assert found_recipe_phases[0].power_level == p_level
        assert found_recipe_phases[0].red_level == r_level
        assert found_recipe_phases[0].blue_level == b_level     

        flag.append(True)

    sio.emit("read_all_entities", {})
    print("WAITING FOR IT!")
    wait_for_event(sio, flag, 1, 5, "test_find_all_entities")
    print("all entities found")


def _test_create_entities(sio):
    rooms = _test_send_room(sio)
    rack = _test_send_rack(sio, rooms[0])
    shelf = _test_send_shelf(sio, rack)
    start = datetime.utcnow() + timedelta(0, 3)
    p_level = 9
    r_level = 8
    b_level = 7
    recipe_phases = [
                {
                    "start_date": start.strftime("%Y-%m-%d %H:%M:%S"),
                    "power_level": p_level,
                    "red_level": r_level,
                    "blue_level": b_level,
                }
            ]

    start_time, end_time, recipe_phases = _test_send_shelf_grow(
        sio, rooms[0].room_id, rack.rack_id, shelf.shelf_id
    )
    _test_find_all_entities(
        sio, rooms, [rack], [shelf], start_time, end_time, p_level, r_level, b_level
    )
    print("create_entities_test passed!")


def _test_room_not_found(sio):
    flag = []

    room_dict = {"room": {"room_id": 5000, "is_on": True}}

    @sio.on("return_room")
    def find_room_listener(message) -> None:
        assert message["room"] is None, "Found a nonexistent room"
        flag.append(True)

    sio.emit("read_room", room_dict)

    wait_for_event(sio, flag, 1, 10, "test_room_not_found")

    print("room not found test passed!")


def _test_racks_not_found_in_room(sio):
    flag = []

    room_dict = {"room": {"room_id": 5000}}

    @sio.on("return_racks_in_room")
    def return_racks_in_room_listener(message) -> None:
        assert message["racks"] == [], "Found nonexistent racks"
        assert message["room_id"] == room_dict["room"]["room_id"]
        flag.append(True)

    sio.emit("read_all_racks_in_room", room_dict)

    wait_for_event(sio, flag, 1, 10, "test_racks_not_found_in_room")

    print("racks not found in room test passed!")


def _test_entities_not_found(sio):
    sio.sleep(1)
    _test_room_not_found(sio)
    _test_racks_not_found_in_room(sio)
    print("entities_not_found_test passed!")


def run_test_and_disconnect(test_func):
    sio = socketio.Client()
    sio.connect("http://sunrisa_server:5000")
    test_func(sio)
    sio.disconnect()


############################################################
#################### PYTEST DEFINITIONS ####################
############################################################


def test_create_entities():
    run_test_and_disconnect(_test_create_entities)
    print("Test create entities passed!")


def test_entities_not_found():
    run_test_and_disconnect(_test_entities_not_found)
    print("Test entities not found passed!")
