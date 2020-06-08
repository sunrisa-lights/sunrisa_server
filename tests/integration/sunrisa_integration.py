import socketio
import pymysql.cursors
import logging
import sys
import time
from datetime import date, datetime, timedelta

from typing import List

# TODO(lwotton): Remove this hack
sys.path.append(".")

from app.db.db import DB
from app.models.room import Room
from app.models.rack import Rack
from app.models.recipe import Recipe
from app.models.schedule import Schedule
from app.models.shelf import Shelf
from app.models.plant import Plant
from app.views.events import NAMESPACE

# standard Python
sio = socketio.Client()
sio.connect("http://localhost:5000")
#sio.connect("https://sunrisalights.com")

expected_processed_entities = None

logging.basicConfig(filename="error.log", level=logging.DEBUG)
db_name = "sunrisa_test"
db = DB(db_name, logging)

test_namespace = '/'


# flag should be an empty list that is populated and has a certain length
def wait_for_event(flag, length_condition, num_seconds, test_name):
    seconds_counter = 0
    while len(flag) != length_condition and seconds_counter < num_seconds:
        time.sleep(1)
        seconds_counter += 1

    assert flag, "Timed out waiting for event for test {}".format(test_name)


def _test_send_room(sio):
    global expected_processed_entities
    expected_processed_entities = ["room"]

    # send initial room update
    room_dict = {"room": {"room_id": 1, "is_on": False, "is_veg_room": True, "brightness": 5}}
    room_dict[NAMESPACE] = test_namespace
    sio.emit("message_sent", room_dict)

    flag = []

    @sio.on("return_room", namespace=test_namespace)
    def find_room_listener(message) -> None:
        print("got message:", message)
        assert 'room' in message
        returned_room = Room.from_json(message["room"])
        expected_room = Room.from_json(room_dict["room"])

        print("returned_room:", returned_room, "expected_room:", expected_room)
        assert returned_room == expected_room
        flag.append(True)

    sio.emit("read_room", room_dict)

    wait_for_event(flag, 1, 5, "test_send_room.create_room")

    print("first room found and returned")

    # update same room to on
    room_dict["room"]["is_on"] = not room_dict["room"]["is_on"]
    sio.emit("message_sent", room_dict)

    sio.emit("read_room", room_dict)

    wait_for_event(flag, 2, 5, "test_send_room.update_room")

    print("second room read and updated")

    # create new room
    room_dict2 = {"room": {"room_id": 2, "is_on": False, "is_veg_room": True, "brightness": 80}, NAMESPACE: test_namespace}
    sio.emit("message_sent", room_dict2)

    # return both rooms
    rooms = []
    @sio.on("return_rooms", namespace=test_namespace)
    def find_all_rooms_listener(message) -> None:
        found_rooms = message['rooms']
        for fr in found_rooms:
            rooms.append(Room.from_json(fr))

        room_map = {room.room_id: room for room in rooms}
        first_id = room_dict['room']['room_id']
        second_id = room_dict2['room']['room_id']
        assert room_map[first_id] == Room.from_json(room_dict['room'])
        assert room_map[second_id] == Room.from_json(room_dict2['room'])

    sio.emit("read_all_rooms", {NAMESPACE: test_namespace})
    wait_for_event(rooms, 2, 5, "test_send_room.read_rooms")
    print("read all rooms")

    return [Room.from_json(room_dict["room"]), Room.from_json(room_dict2['room'])]


def _test_send_rack(sio, room):
    global expected_processed_entities
    expected_processed_entities = ["rack"]

    # send initial rack update with created room id
    rack_dict = {
            "rack": {"rack_id": 2, "room_id": room.room_id, "voltage": 100, "is_on": True, "is_connected": True},
            NAMESPACE: test_namespace,
    }
    sio.emit("message_sent", rack_dict)

    flag = []

    @sio.on("return_racks_in_room", namespace=test_namespace)
    def return_racks_in_room_listener(message) -> None:
        found_racks = message['racks']
        room_id = message['room_id']

        print("found_racks:", found_racks, rack_dict)
        assert len(found_racks) == 1
        assert Rack.from_json(found_racks[0]) == Rack.from_json(rack_dict['rack'])
        assert room_id == room.room_id

        flag.append(True)

    sio.emit("read_all_racks_in_room", {'room': {'room_id': room.room_id}, NAMESPACE: test_namespace})
    wait_for_event(flag, 1, 5, "test_send_rack.read_all_racks_in_room.1")

    print("first rack found and returned")

    # update same rack to on
    rack_dict["rack"]["is_on"] = not rack_dict["rack"]["is_on"]
    sio.emit("message_sent", rack_dict)
    sio.emit("read_all_racks_in_room", {'room': {'room_id': room.room_id}, NAMESPACE: test_namespace})
    wait_for_event(flag, 2, 5, "test_send_rack.read_all_racks_in_room.2")

    print("second rack found and returned")

    return Rack.from_json(rack_dict["rack"])


def _test_send_recipe(sio):
    global expected_processed_entities
    expected_processed_entities = ["recipe"]

    recipe_dict = {
        "recipe": {
            "recipe_id": 1,
            "recipe_name": "purp",
            "power_level": 1000,
            "red_level": 10,
            "blue_level": 20,
            "num_hours": 20000,
        },
        NAMESPACE: test_namespace,
    }
    sio.emit("message_sent", recipe_dict)
    sio.sleep(1)
    get_recipe_sql = "SELECT recipe_id, recipe_name, power_level, red_level, blue_level, num_hours FROM recipes WHERE recipe_id={}".format(
        recipe_dict["recipe"]["recipe_id"]
    )
    with db._new_connection(db_name) as cursor:
        cursor.execute(get_recipe_sql)
        (
            recipe_id,
            recipe_name,
            power_level,
            red_level,
            blue_level,
            num_hours,
        ) = cursor.fetchone()
        foundRecipe = Recipe(
            recipe_id, recipe_name, power_level, red_level, blue_level, num_hours
        )
        expected = Recipe.from_json(recipe_dict["recipe"])
        print("foundRecipe:", foundRecipe, "expected:", expected)
        assert foundRecipe == expected

        return foundRecipe


def _test_send_shelf(sio, rack, recipe):
    global expected_processed_entities
    expected_processed_entities = ["shelf"]

    shelf_dict = {
        "shelf": {"shelf_id": 1, "rack_id": rack.rack_id, "recipe_id": recipe.recipe_id},
        NAMESPACE: test_namespace,
    }
    sio.emit("message_sent", shelf_dict)
    sio.sleep(1)
    get_shelf_sql = "SELECT shelf_id, rack_id, recipe_id, power_level, red_level, blue_level FROM shelves WHERE shelf_id={}".format(
        shelf_dict["shelf"]["shelf_id"]
    )
    with db._new_connection(db_name) as cursor:
        cursor.execute(get_shelf_sql)
        shelf_id, rack_id, recipe_id, power_level, red_level, blue_level = cursor.fetchone()
        foundShelf = Shelf(shelf_id, rack_id, recipe_id, power_level, red_level, blue_level)
        expected = Shelf.from_json(shelf_dict["shelf"])
        print("foundShelf:", foundShelf, "expected:", expected)
        assert foundShelf == expected

        return foundShelf


def _test_send_plant(sio, shelf):
    global expected_processed_entities
    expected_processed_entities = ["plant"]

    # initially leave shelf_id nil to test out nil shelf
    plant_dict = {"plant": {"olcc_number": 1}, NAMESPACE: test_namespace}
    sio.emit("message_sent", plant_dict)
    sio.sleep(1)
    get_plant_sql = "SELECT olcc_number, shelf_id FROM plants WHERE olcc_number={}".format(
        plant_dict["plant"]["olcc_number"]
    )
    with db._new_connection(db_name) as cursor:
        cursor.execute(get_plant_sql)
        olcc_number, shelf_id = cursor.fetchone()
        foundPlant = Plant(olcc_number, shelf_id)
        expected = Plant.from_json(plant_dict["plant"])
        print("foundPlant:", foundPlant, "expected:", expected)
        assert foundPlant == expected

    # add shelf in and verify that it is updated properly
    plant_dict = {"plant": {"olcc_number": 1, "shelf_id": shelf.shelf_id}, NAMESPACE: test_namespace}
    sio.emit("message_sent", plant_dict)
    sio.sleep(1)
    get_plant_sql = "SELECT olcc_number, shelf_id FROM plants WHERE olcc_number={}".format(
        plant_dict["plant"]["olcc_number"]
    )
    with db._new_connection(db_name) as cursor:
        cursor.execute(get_plant_sql)
        olcc_number, shelf_id = cursor.fetchone()
        foundPlant = Plant(olcc_number, shelf_id)
        expected = Plant.from_json(plant_dict["plant"])
        print("foundPlant:", foundPlant, "expected:", expected)
        assert foundPlant == expected

        return foundPlant


def _test_send_room_schedule(sio, room_id):
    start = datetime.now() + timedelta(0, 3) # 3 seconds from now
    end = start + timedelta(0, 2) # 5 seconds from now

    start_time = start.strftime('%Y-%m-%d %H:%M:%S')
    end_time = end.strftime('%Y-%m-%d %H:%M:%S')

    room_schedule = Schedule.from_json({"room_id": room_id, 'start_datetime': start_time, 'end_datetime': end_time, 'power_level': 1, 'red_level': 2, 'blue_level': 3})
    print("Created schedule")

    schedule_dict = {"schedule": room_schedule.to_json(), NAMESPACE: test_namespace}

    flag = []

    @sio.on("set_lights_for_room", namespace=test_namespace)
    def set_lights_for_room(message) -> None:
        assert 'schedule' in message
        room_dict = message['schedule']
        if len(flag) == 0:
            assert room_schedule.room_id == room_dict['room_id']
            assert room_schedule.power_level == room_dict['power_level']
            assert room_schedule.red_level == room_dict['red_level']
            assert room_schedule.blue_level == room_dict['blue_level']
        elif len(flag) == 1:
            assert room_schedule.room_id == room_dict['room_id']
            assert room_schedule.power_level == 0
            assert room_schedule.red_level == 0
            assert room_schedule.blue_level == 0

        flag.append(True)

    sio.emit('post_room_schedule', schedule_dict)
    wait_for_event(flag, 2, 10, "test_post_room_schedule")

    print("test send room schedule passed")

    @sio.on("get_current_room_schedules_succeeded", namespace=test_namespace)
    def get_current_room_schedules(message) -> None:
        assert message['succeeded']
        assert 'current_room_schedules' in message

        schedule_json_list = message['current_room_schedules']
        schedules = [Schedule.from_json(s) for s in schedule_json_list]

        assert len(schedules) == 1
        assert room_schedule == schedules[0]

    sio.emit('get_current_room_schedules', {'room': {'room_id': room_id}})
    wait_for_event(flag, 3, 5, "test_get_room_schedules")

    print("test get room schedules passed")

def _test_find_all_entities(sio, rooms: List[Room], racks: List[Rack]):
    entities = []
    for room in rooms:
        room_json = room.to_json()
        racks_json = [rack.to_json() for rack in racks if rack.room_id == room.room_id]
        room_json['racks'] = racks_json
        entities.append(room_json)

    def ordered(obj):
        if isinstance(obj, dict):
            return sorted((k, ordered(v)) for k, v in obj.items())
        elif isinstance(obj, list):
            return sorted(ordered(x) for x in obj)
        else:
            return obj

    flag = []

    @sio.on("return_all_entities", namespace=test_namespace)
    def return_all_entities_listener(message) -> None:
        print("Received message in entities_listener:", message, "expected:", entities)
        assert 'rooms' in message
        assert ordered(message['rooms']) == ordered(entities)

        flag.append(True)

    sio.emit("read_all_entities", {NAMESPACE: test_namespace})
    wait_for_event(flag, 1, 5, "test_find_all_entities")
    print("all entities found")


def _test_create_entities(sio):
    @sio.on("message_received", namespace=test_namespace)
    def verify_message_received(entities_processed):
        assert entities_processed["processed"] == expected_processed_entities

    rooms = _test_send_room(sio)
    rack = _test_send_rack(sio, rooms[0])
    recipe = _test_send_recipe(sio)
    shelf = _test_send_shelf(sio, rack, recipe)
    _test_send_plant(sio, shelf)
    _test_send_room_schedule(sio, rooms[0].room_id)
    _test_find_all_entities(sio, rooms, [rack])
    print("create_entities_test passed!")


def _test_room_not_found(sio):
    flag = []

    room_dict = {'room': {'room_id': 5000, 'is_on': True}, NAMESPACE: test_namespace}

    @sio.on("return_room", namespace=test_namespace)
    def find_room_listener(message) -> None:
        assert message['room'] is None, "Found a nonexistent room"
        flag.append(True)

    sio.emit("read_room", room_dict)

    wait_for_event(flag, 1, 5, "test_room_not_found")

    print("room not found test passed!")


def _test_racks_not_found_in_room(sio):
    flag = []

    room_dict = {'room': {'room_id': 5000}, NAMESPACE: test_namespace}

    @sio.on("return_racks_in_room", namespace=test_namespace)
    def return_racks_in_room_listener(message) -> None:
        assert message['racks'] == [], "Found nonexistent racks"
        assert message['room_id'] == room_dict['room']['room_id']
        flag.append(True)

    sio.emit("read_all_racks_in_room", room_dict)

    wait_for_event(flag, 1, 5, "test_racks_not_found_in_room")

    print("racks not found in room test passed!")

def _test_entities_not_found(sio):
    sio.sleep(5)
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
