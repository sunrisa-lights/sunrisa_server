import socketio
import pymysql.cursors
import logging
import sys
import time
from datetime import date, datetime

# TODO(lwotton): Remove this hack
sys.path.append(".")

from app.db.db import DB
from app.models.room import Room
from app.models.rack import Rack
from app.models.recipe import Recipe
from app.models.shelf import Shelf
from app.models.plant import Plant

# standard Python
sio = socketio.Client()
sio.connect("http://localhost:5000")

expected_processed_entities = None

conn = pymysql.connect(host="localhost", user="root", password="root")
conn.autocommit(True)  # necessary so we don't get stale reads back
logging.basicConfig(filename="error.log", level=logging.DEBUG)
db_name = "sunrisa_test"
db = DB(conn, db_name, logging)


# flag should be an empty list that is populated and has a certain length
def wait_for_event(flag, length_condition, num_seconds, test_name):
    seconds_counter = 0
    while len(flag) != length_condition and seconds_counter < num_seconds:
        time.sleep(1)
        seconds_counter += 1

    assert flag, "Timed out waiting for event for test {}".format(test_name)


def test_send_room(sio):
    global expected_processed_entities
    expected_processed_entities = ["room"]

    # send initial room update
    room_dict = {"room": {"room_id": 1, "is_on": False, "is_veg_room": True}}
    sio.emit("message_sent", room_dict)

    flag = []

    @sio.on("return_room")
    def find_room_listener(message) -> None:
        returned_room = Room.from_json(message["room"])
        expected_room = Room.from_json(room_dict["room"])

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
    room_dict2 = {"room": {"room_id": 2, "is_on": False, "is_veg_room": True}}
    sio.emit("message_sent", room_dict2)

    # return both rooms
    rooms = []
    @sio.on("return_rooms")
    def find_all_rooms_listener(message) -> None:
        found_rooms = message['rooms']
        for fr in found_rooms:
            rooms.append(Room.from_json(fr))

        room_map = {room.room_id: room for room in rooms}
        first_id = room_dict['room']['room_id']
        second_id = room_dict2['room']['room_id']
        assert room_map[first_id] == Room.from_json(room_dict['room'])
        assert room_map[second_id] == Room.from_json(room_dict2['room'])

    sio.emit("read_all_rooms", {})
    wait_for_event(rooms, 2, 5, "test_send_room.read_rooms")
    print("read all rooms")

    return Room.from_json(room_dict["room"])


def test_send_rack(sio, room):
    global expected_processed_entities
    expected_processed_entities = ["rack"]

    # send initial rack update with created room id
    rack_dict = {
        "rack": {"rack_id": 2, "room_id": room.room_id, "voltage": 100, "is_on": True}
    }
    sio.emit("message_sent", rack_dict)
    sio.sleep(1)  # wait for changes to propagate in the DB
    get_rack_sql = "SELECT rack_id, room_id, voltage, is_on, is_connected FROM racks WHERE rack_id={}".format(
        rack_dict["rack"]["rack_id"]
    )
    with conn.cursor() as cursor:
        cursor.execute(get_rack_sql)
        rack_id, room_id, voltage, is_on, is_connected = cursor.fetchone()
        foundRack = Rack(rack_id, room_id, voltage, bool(is_on), bool(is_connected))
        expected = Rack.from_json(rack_dict["rack"])
        print("foundRack:", foundRack, "expected:", expected)
        assert foundRack == expected

    # update same rack to on
    rack_dict["rack"]["is_on"] = not rack_dict["rack"]["is_on"]
    sio.emit("message_sent", rack_dict)
    sio.sleep(1)  # wait for changes to propagate in the DB
    get_rack_sql = "SELECT rack_id, room_id, voltage, is_on, is_connected FROM racks WHERE rack_id={}".format(
        rack_dict["rack"]["rack_id"]
    )
    with conn.cursor() as cursor:
        cursor.execute(get_rack_sql)
        rack_id, room_id, voltage, is_on, is_connected = cursor.fetchone()
        foundRack = Rack(rack_id, room_id, voltage, bool(is_on), bool(is_connected))
        expected = Rack.from_json(rack_dict["rack"])
        print("foundRack:", foundRack, "expected:", expected)
        assert foundRack == expected

        return foundRack


def test_send_recipe(sio):
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
        }
    }
    sio.emit("message_sent", recipe_dict)
    sio.sleep(1)
    get_recipe_sql = "SELECT recipe_id, recipe_name, power_level, red_level, blue_level, num_hours FROM recipes WHERE recipe_id={}".format(
        recipe_dict["recipe"]["recipe_id"]
    )
    with conn.cursor() as cursor:
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


def test_send_shelf(sio, rack, recipe):
    global expected_processed_entities
    expected_processed_entities = ["shelf"]

    # initially leave recipe_id nil to test out nil recipe
    shelf_dict = {"shelf": {"shelf_id": 1, "rack_id": rack.rack_id}}
    sio.emit("message_sent", shelf_dict)
    sio.sleep(1)
    get_shelf_sql = "SELECT shelf_id, rack_id, recipe_id FROM shelves WHERE shelf_id={}".format(
        shelf_dict["shelf"]["shelf_id"]
    )
    with conn.cursor() as cursor:
        cursor.execute(get_shelf_sql)
        shelf_id, rack_id, recipe_id = cursor.fetchone()
        foundShelf = Shelf(shelf_id, rack_id, recipe_id)
        expected = Shelf.from_json(shelf_dict["shelf"])
        print("foundShelf:", foundShelf, "expected:", expected)
        assert foundShelf == expected

    # add recipe in and verify that it is updated properly
    shelf_dict = {
        "shelf": {"shelf_id": 1, "rack_id": rack.rack_id, "recipe_id": recipe.recipe_id}
    }
    sio.emit("message_sent", shelf_dict)
    sio.sleep(1)
    get_shelf_sql = "SELECT shelf_id, rack_id, recipe_id FROM shelves WHERE shelf_id={}".format(
        shelf_dict["shelf"]["shelf_id"]
    )
    with conn.cursor() as cursor:
        cursor.execute(get_shelf_sql)
        shelf_id, rack_id, recipe_id = cursor.fetchone()
        foundShelf = Shelf(shelf_id, rack_id, recipe_id)
        expected = Shelf.from_json(shelf_dict["shelf"])
        print("foundShelf:", foundShelf, "expected:", expected)
        assert foundShelf == expected

        return foundShelf


def test_send_plant(sio, shelf):
    global expected_processed_entities
    expected_processed_entities = ["plant"]

    # initially leave shelf_id nil to test out nil shelf
    plant_dict = {"plant": {"olcc_number": 1}}
    sio.emit("message_sent", plant_dict)
    sio.sleep(1)
    get_plant_sql = "SELECT olcc_number, shelf_id FROM plants WHERE olcc_number={}".format(
        plant_dict["plant"]["olcc_number"]
    )
    with conn.cursor() as cursor:
        cursor.execute(get_plant_sql)
        olcc_number, shelf_id = cursor.fetchone()
        foundPlant = Plant(olcc_number, shelf_id)
        expected = Plant.from_json(plant_dict["plant"])
        print("foundPlant:", foundPlant, "expected:", expected)
        assert foundPlant == expected

    # add shelf in and verify that it is updated properly
    plant_dict = {"plant": {"olcc_number": 1, "shelf_id": shelf.shelf_id}}
    sio.emit("message_sent", plant_dict)
    sio.sleep(1)
    get_plant_sql = "SELECT olcc_number, shelf_id FROM plants WHERE olcc_number={}".format(
        plant_dict["plant"]["olcc_number"]
    )
    with conn.cursor() as cursor:
        cursor.execute(get_plant_sql)
        olcc_number, shelf_id = cursor.fetchone()
        foundPlant = Plant(olcc_number, shelf_id)
        expected = Plant.from_json(plant_dict["plant"])
        print("foundPlant:", foundPlant, "expected:", expected)
        assert foundPlant == expected

        return foundPlant

def test_send_schedule(sio, shelf_id):
    global expected_processed_entities
    expected_processed_entities = ["schedule"]

    start = datetime.now()
    end = date(2021, 4, 13)

    start_time = start.strftime('%Y-%m-%d %H:%M:%S')
    end_time = end.strftime('%Y-%m-%d %H:%M:%S')

    schedule_dict = {"schedule": {"shelf_id": shelf_id, 'start_time': start_time, 'end_time': end_time}}
    sio.emit("message_sent", schedule_dict)
    sio.sleep(1)
    get_schedule_sql = "SELECT shelf_id, start_time, end_time FROM schedules WHERE shelf_id={} AND start_time='{}' AND end_time='{}'".format(
        schedule_dict["schedule"]["shelf_id"], schedule_dict["schedule"]["start_time"], schedule_dict["schedule"]["end_time"]
    )
    with conn.cursor() as cursor:
        cursor.execute(get_schedule_sql)
        shelf_id, start_time, end_time = cursor.fetchone()
        print("foundSchedule:", (shelf_id, start_time, end_time), "expected:", schedule_dict["schedule"])
        assert shelf_id == schedule_dict["schedule"]["shelf_id"]
        assert start_time.strftime('%Y-%m-%d %H:%M:%S') == schedule_dict["schedule"]["start_time"]
        assert end_time.strftime('%Y-%m-%d %H:%M:%S') == schedule_dict["schedule"]["end_time"]


def create_entities_test(sio):
    @sio.on("message_received")
    def verify_message_received(entities_processed):
        assert entities_processed["processed"] == expected_processed_entities

    room = test_send_room(sio)
    rack = test_send_rack(sio, room)
    recipe = test_send_recipe(sio)
    shelf = test_send_shelf(sio, rack, recipe)
    test_send_plant(sio, shelf)
    test_send_schedule(sio, shelf.shelf_id)
    print("create_entities_test passed!")

def test_room_not_found(sio):
    flag = []

    room_dict = {'room': {'room_id': 5000, 'is_on': True}}

    @sio.on("return_room")
    def find_room_listener(message) -> None:
        assert message['room'] is None, "Found a nonexistent room"
        flag.append(True)

    sio.emit("read_room", room_dict)

    wait_for_event(flag, 1, 5, "test_send_room.create_room")


def entities_not_found_test(sio):
    test_room_not_found(sio)
    print("entities_not_found_test passed!")

def run_tests():
    def run_test_and_disconnect(test_func):
        sio = socketio.Client()
        sio.connect("http://localhost:5000")
        test_func(sio)
        sio.disconnect()

    run_test_and_disconnect(create_entities_test)
    run_test_and_disconnect(entities_not_found_test)
    print("Integration tests passed!")


if __name__ == "__main__":
    run_tests()

    # sleep because we get BrokenPipeError when we disconnect too fast after sending events
    sio.sleep(2)

    sio.disconnect()
