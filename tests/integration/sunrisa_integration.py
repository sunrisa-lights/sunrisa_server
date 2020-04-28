import socketio
import pymysql.cursors
import logging
import sys

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
# sio.connect("https://sunrisalights.com")

expected_processed_entities = None

conn = pymysql.connect(host="localhost", user="root", password="root")
conn.autocommit(True)  # necessary so we don't get stale reads back
logging.basicConfig(filename="error.log", level=logging.DEBUG)
db_name = "sunrisa_test"
db = DB(conn, db_name, logging)


def test_send_room():
    global expected_processed_entities
    expected_processed_entities = ["room"]

    # send initial room update
    room_dict = {"room": {"room_id": 1, "is_on": False, "is_veg_room": True}}
    sio.emit("message_sent", room_dict)

    num_events_emitted = 0

    @sio.on("return_room")
    def find_room_listener(message) -> None:
        nonlocal num_events_emitted
        returned_room = Room.from_json(message["room"])
        expected_room = Room.from_json(room_dict["room"])

        assert returned_room == expected_room
        num_events_emitted += 1

    sio.emit("read_room", room_dict)
    num_seconds = 0
    while num_events_emitted == 0 and num_seconds < 5:
        sio.sleep(1)
        num_seconds += 1

    assert (
        num_events_emitted == 1
    ), "waiting for 1st room read event timed out after 5 seconds"

    # update same room to on
    room_dict["room"]["is_on"] = not room_dict["room"]["is_on"]
    sio.emit("message_sent", room_dict)

    sio.emit("read_room", room_dict)
    num_seconds = 0
    while num_events_emitted == 1 and num_seconds < 5:
        sio.sleep(1)
        num_seconds += 1

    assert (
        num_events_emitted == 2
    ), "waiting for 2nd room read event timed out after 5 seconds"

    return Room.from_json(room_dict["room"])


def test_send_rack(room):
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


def test_send_recipe():
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


def test_send_shelf(rack, recipe):
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


def test_send_plant(shelf):
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


@sio.on("message_received")
def verify_message_received(entities_processed):
    assert entities_processed["processed"] == expected_processed_entities


def run_tests():
    room = test_send_room()
    rack = test_send_rack(room)
    recipe = test_send_recipe()
    shelf = test_send_shelf(rack, recipe)
    test_send_plant(shelf)
    print("Integration tests passed!")


if __name__ == "__main__":
    run_tests()

    # sleep because we get BrokenPipeError when we disconnect too fast after sending events
    sio.sleep(2)

    sio.disconnect()
