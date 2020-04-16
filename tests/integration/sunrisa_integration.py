import socketio
import pymysql.cursors
import logging
import sys
# TODO(lwotton): Remove this hack
sys.path.append('.')

from app.db.db import DB
from app.models.room import Room
from app.models.rack import Rack

# standard Python
sio = socketio.Client()
sio.connect('http://localhost:5000')

expected_processed_entities = None

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='root')
conn.autocommit(True) # necessary so we don't get stale reads back
logging.basicConfig(filename='error.log',level=logging.DEBUG)
db_name = "sunrisa_test"
db = DB(conn, db_name, logging)

def test_send_room():
    global expected_processed_entities
    expected_processed_entities = ['room']

    # send initial room update
    room_dict = {'room': {'roomId': 1, 'isOn': False, 'isVegRoom': True}}
    sio.emit('message_sent', room_dict)
    sio.sleep(1) # wait for changes to propagate in the DB
    get_room_sql = "SELECT room_id, is_on, is_veg_room FROM rooms WHERE room_id={}".format(room_dict['room']['roomId'])
    with conn.cursor() as cursor:
        cursor.execute(get_room_sql)
        rid, is_on, is_veg = cursor.fetchone()
        foundRoom = Room(rid, bool(is_on), bool(is_veg))
        expected = Room.from_json(room_dict['room'])
        print("foundRoom:", foundRoom, "expected:", expected)
        assert foundRoom == expected

    # update same room to on
    room_dict['room']['isOn'] = not room_dict['room']['isOn']
    sio.emit('message_sent', room_dict)
    sio.sleep(1) # wait for changes to propagate in the DB
    get_room_sql = "SELECT room_id, is_on, is_veg_room FROM rooms WHERE room_id={}".format(room_dict['room']['roomId'])
    with conn.cursor() as cursor:
        cursor.execute(get_room_sql)
        rid, is_on, is_veg = cursor.fetchone()
        foundRoom = Room(rid, bool(is_on), bool(is_veg))
        expected = Room.from_json(room_dict['room'])
        print("foundRoom:", foundRoom, "expected:", expected)
        assert foundRoom == expected

    return foundRoom

def test_send_rack(room):
    global expected_processed_entities
    expected_processed_entities = ['rack']

    # send initial rack update with created room id
    rack_dict = {'rack': {'rack_id': 2, 'room_id': room.roomId, 'voltage': 100, 'is_on': True}}
    sio.emit('message_sent', rack_dict)
    sio.sleep(1) # wait for changes to propagate in the DB
    get_rack_sql = "SELECT rack_id, room_id, voltage, is_on, is_connected FROM racks WHERE rack_id={}".format(rack_dict['rack']['rack_id'])
    with conn.cursor() as cursor:
        cursor.execute(get_rack_sql)
        rack_id, room_id, voltage, is_on, is_connected = cursor.fetchone()
        foundRack = Rack(rack_id, room_id, voltage, bool(is_on), bool(is_connected))
        expected = Rack.from_json(rack_dict['rack'])
        print("foundRack:", foundRack, "expected:", expected)
        assert foundRack == expected

    # update same room to on
    rack_dict['rack']['is_on'] = not rack_dict['rack']['is_on']
    sio.emit('message_sent', rack_dict)
    sio.sleep(1) # wait for changes to propagate in the DB
    get_rack_sql = "SELECT rack_id, room_id, voltage, is_on, is_connected FROM racks WHERE rack_id={}".format(rack_dict['rack']['rack_id'])
    with conn.cursor() as cursor:
        cursor.execute(get_rack_sql)
        rack_id, room_id, voltage, is_on, is_connected = cursor.fetchone()
        foundRack = Rack(rack_id, room_id, voltage, bool(is_on), bool(is_connected))
        expected = Rack.from_json(rack_dict['rack'])
        print("foundRack:", foundRack, "expected:", expected)
        assert foundRack == expected


def test_send_recipe():
    global expected_processed_entities
    expected_processed_entities = ['recipe']

    recipe_dict = {'recipe': {'recipe_id': 1, 'recipe_name': 'purp', 'power_level': 1000, 'red_level': 10, 'blue_level': 20, 'num_hours': 20000}}
    sio.emit('message_sent', recipe_dict)
    sio.sleep(1)
    recipe = Recipe.from_json({'recipe_id': 1, 'recipe_name': 'purp', 'power_level': 1000, 'red_level': 10, 'blue_level': 20, 'num_hours': 20000})
    get_recipe_sql = "SELECT recipe_id, recipe_name, power_level, red_level, blue_level, num_hours FROM recipes WHERE recipe_id={}".format(rack_dict['recipe']['recipe_id'])
    with conn.cursor() as cursor:
        cursor.execute(get_recipe_sql)
        recipe_id, recipe_name, power_level, red_level, blue_level, num_hours = cursor.fetchone()
        foundRecipe = Recipe(recipe_id, recipe_name, power_level, red_level, blue_level, num_hours)
        expected = Recipe.from_json(recipe_dict['recipe'])
        print("foundRecipe:", foundRecipe, "expected:", expected)
        assert foundRecipe == expected


@sio.on('message_received')
def verify_message_received(entities_processed):
    assert entities_processed['processed'] == expected_processed_entities

def run_tests():
    createdRoom = test_send_room()
    test_send_rack(createdRoom)
    test_send_recipe()
    print("Integration tests passed!")

if __name__ == "__main__":
    run_tests()

    # sleep because we get BrokenPipeError when we disconnect too fast after sending events
    sio.sleep(2)

    sio.disconnect()
