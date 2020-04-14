import socketio
import pymysql.cursors
import logging
import sys
# TODO(lwotton): Remove this hack
sys.path.append('.')

from app.db.db import DB
from app.models.room import Room

# standard Python
sio = socketio.Client()
sio.connect('http://localhost:5000')

expected_processed_entities = None

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='root')
logging.basicConfig(filename='error.log',level=logging.DEBUG)
db_name = "sunrisa_test"
db = DB(conn, db_name, logging)

def test_send_room():
    global expected_processed_entities
    expected_processed_entities = ['room']

    # send initial room update
    room_dict = {'room': {'roomId': 1, 'isOn': False, 'isVegRoom': True}}
    sio.emit('message_sent', room_dict)
    sio.sleep(10) # wait for changes to propagate in the DB
    get_room_sql = "SELECT room_id, is_on, is_veg_room FROM rooms WHERE room_id={}".format(room_dict['room']['roomId'])
    with conn.cursor() as cursor:
        cursor.execute(get_room_sql)
        rid, is_on, is_veg = cursor.fetchone()
        foundRoom = Room(rid, bool(is_on), bool(is_veg))
        expected = Room.from_json(room_dict['room'])
        print("foundRoom:", foundRoom, "expected:", expected)
        assert foundRoom == Room.from_json(room_dict['room'])

    # update same room to on
    room_dict['room']['isOn'] = True
    sio.emit('message_sent', room_dict)
    sio.sleep(10) # wait for changes to propagate in the DB
    get_room_sql = "SELECT room_id, is_on, is_veg_room FROM rooms WHERE room_id={}".format(room_dict['room']['roomId'])
    with conn.cursor() as cursor:
        cursor.execute(get_room_sql)
        rid, is_on, is_veg = cursor.fetchone()
        foundRoom = Room(rid, bool(is_on), bool(is_veg))
        expected = Room.from_json(room_dict['room'])
        print("foundRoom:", foundRoom, "expected:", expected)
        assert foundRoom == Room.from_json(room_dict['room'])


@sio.on('message_received')
def verify_message_received(entities_processed):
    assert entities_processed['processed'] == expected_processed_entities

def run_tests():
    test_send_room()
    print("Integration tests passed!")

if __name__ == "__main__":
    run_tests()

    # sleep because we get BrokenPipeError when we disconnect too fast after sending events
    sio.sleep(2)

    sio.disconnect()
