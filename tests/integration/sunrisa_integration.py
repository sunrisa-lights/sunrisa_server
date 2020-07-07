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

from app.db.db import DB
from app.models.grow import Grow
from app.models.room import Room
from app.models.rack import Rack
from app.models.recipe import Recipe
from app.models.recipe_phase import RecipePhase
from app.models.shelf import Shelf
from app.models.plant import Plant

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
    sio.sleep(10)

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
    sio.sleep(10)

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


def _test_send_recipe(sio):
    recipe_dict = {
        "recipe": {
            "recipe_id": 1,
            "recipe_name": "purp",
            "recipe_phases": [
                {
                    "recipe_id": 1,
                    "recipe_phase_num": 1,
                    "num_hours": 10,
                    "power_level": 9,
                    "red_level": 8,
                    "blue_level": 7,
                },
                {
                    "recipe_id": 1,
                    "recipe_phase_num": 2,
                    "num_hours": 69,
                    "power_level": 69,
                    "red_level": 68,
                    "blue_level": 67,
                },
            ],
        },
    }

    flag = []

    @sio.on("create_new_recipe_response")
    def create_new_recipe_response(message) -> None:
        assert "succeeded" in message
        assert message["succeeded"]

        flag.append(True)

    sio.emit("create_new_recipe", recipe_dict)
    wait_for_event(sio, flag, 1, 5, "test_create_recipe_with_phases")
    print("Created new recipe with phases")

    recipe = Recipe.from_json(recipe_dict["recipe"])
    recipe_phases = [RecipePhase.from_json(recipe_dict["recipe"]["recipe_phases"][0])]

    return recipe, recipe_phases


def _test_send_shelf(sio, rack, recipe):
    shelf_dict = {
        "shelf": {"shelf_id": 1, "rack_id": rack.rack_id,},
    }
    sio.emit("message_sent", shelf_dict)
    sio.sleep(1)
    expected = Shelf.from_json(shelf_dict["shelf"])

    return expected


def _test_send_plant(sio, shelf):
    # initially leave shelf_id nil to test out nil shelf
    plant_dict = {"plant": {"olcc_number": 1}}
    sio.emit("message_sent", plant_dict)
    sio.sleep(1)

    # add shelf in and verify that it is updated properly
    plant_dict = {
        "plant": {"olcc_number": 1, "shelf_id": shelf.shelf_id},
    }
    sio.emit("message_sent", plant_dict)
    sio.sleep(1)
    expected = Plant.from_json(plant_dict["plant"])

    return expected


def _test_send_shelf_grow(sio, room_id, rack_id, shelf_id, recipe_phases):
    assert len(recipe_phases) == 1  # only support 1 phase for now

    print("Sending shelf grow")
    start = datetime.utcnow() + timedelta(0, 3)  # 3 seconds from now
    end = start + timedelta(0, 2)  # 5 seconds from now
    print(start)
    print(end)
    start_time = start.strftime("%Y-%m-%d %H:%M:%S")
    end_time = end.strftime("%Y-%m-%d %H:%M:%S")
    print(start_time)
    print(end_time)

    shelf_grows = []
    for rp in recipe_phases:

        shelf_grow = Grow.from_json(
            {
                "room_id": room_id,
                "rack_id": rack_id,
                "shelf_id": shelf_id,
                "recipe_id": rp.recipe_id,
                "recipe_phase_num": rp.recipe_phase_num,
                "start_datetime": start_time,
                "end_datetime": end_time,
            }
        )
        print(shelf_grow.start_datetime)
        print(shelf_grow.end_datetime)
        shelf_grows.append(shelf_grow)

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

    sio.emit("start_grows_for_shelves", {"grows": [s.to_json() for s in shelf_grows]})
    wait_for_event(sio, flag, 1, 5, "test_start_grows_for_shelves")

    for i in range(len(shelf_grows)):
        wait_for_event(sio, flag, i + 2, 5, "test_set_lights_for_grow_job")

    print("test send shelf grow passed")
    return shelf_grow


def _test_find_all_entities(
    sio,
    rooms: List[Room],
    racks: List[Rack],
    shelves: List[Shelf],
    grows: List[Grow],
    recipes: List[Recipe],
    recipe_phases: List[RecipePhase],
):
    flag = []

    @sio.on("return_all_entities")
    def return_all_entities_listener(message) -> None:
        print("Received message in entities_listener:", message)
        assert "rooms" in message
        assert "racks" in message
        assert "shelves" in message
        assert "grows" in message
        assert "recipes" in message
        assert "recipe_phases" in message

        found_rooms = [Room.from_json(r) for r in message["rooms"]]
        found_racks = [Rack.from_json(r) for r in message["racks"]]
        found_shelves = [Shelf.from_json(s) for s in message["shelves"]]
        found_grows = [Grow.from_json(g) for g in message["grows"]]
        found_recipes = [Recipe.from_json(r) for r in message["recipes"]]
        found_recipe_phases = [
            RecipePhase.from_json(rp) for rp in message["recipe_phases"]
        ]

        assert collections.Counter(found_rooms) == collections.Counter(rooms)
        assert collections.Counter(found_racks) == collections.Counter(racks)
        assert collections.Counter(found_shelves) == collections.Counter(shelves)
        print(collections.Counter(found_grows))
        print(collections.Counter(grows))
        assert collections.Counter(found_grows) == collections.Counter(grows)
        assert collections.Counter(found_recipes) == collections.Counter(recipes)
        assert collections.Counter(found_recipe_phases) == collections.Counter(
            recipe_phases
        )

        flag.append(True)

    sio.emit("read_all_entities", {})
    print("WAITING FOR IT!")
    wait_for_event(sio, flag, 1, 5, "test_find_all_entities")
    print("all entities found")


def _test_create_entities(sio):
    rooms = _test_send_room(sio)
    rack = _test_send_rack(sio, rooms[0])
    recipe, recipe_phases = _test_send_recipe(sio)
    shelf = _test_send_shelf(sio, rack, recipe)
    _test_send_plant(sio, shelf)
    grow = _test_send_shelf_grow(
        sio, rooms[0].room_id, rack.rack_id, shelf.shelf_id, recipe_phases
    )
    print("grow", grow)
    _test_find_all_entities(
        sio, rooms, [rack], [shelf], [grow], [recipe], recipe_phases
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


def test_integration():
    def run_test_and_disconnect(test_func):
        sio = socketio.Client()
        sio.connect("http://localhost:5000")
        test_func(sio)
        sio.disconnect()

    run_test_and_disconnect(_test_create_entities)
    run_test_and_disconnect(_test_entities_not_found)
    print("Integration tests passed!")
