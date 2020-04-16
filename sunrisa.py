from flask import Flask, render_template
import pymysql.cursors
import logging
from flask_socketio import SocketIO, emit # type: ignore
from app.models.room import Room
from app.models.rack import Rack
from app.models.recipe import Recipe
from app.models.shelf import Shelf
from app.models.plant import Plant

from app_config import AppConfig

app = Flask(__name__)
socketio = SocketIO(app)

env = "development" # TODO(lwotton): Get to a production environment
appConfig = AppConfig(socketio, env)


@app.route("/", methods=['GET', 'POST'])
def hello():
    logging.debug("Hello was called")
    return render_template('index.html')

@app.route("/pp", methods=['GET'])
def test_write():
    logging.debug("test_write was called")
    return 'hello world'

@socketio.on('connect')
def connect():
    print("I'm connected!")

@socketio.on('connect_error')
def connect_error():
    print("The connection failed!")

@socketio.on('disconnect')
def disconnect():
    print("I'm disconnected!")

@socketio.on('message_sent')
def log_changes(message):
    logging.debug("message sent:", message)
    entities_processed = []

    print("message:", message)
    if 'room' in message:
        # a room is contained in this update
        entities_processed.append('room')
        room_json = message['room']
        room = Room.from_json(room_json)
        appConfig.logger.debug(room)
        print("Saw room in message")
        appConfig.db.write_room(room)

    if 'rack' in message:
        # a rack is contained in this update
        entities_processed.append('rack')
        rack_json = message['rack']
        rack = Rack.from_json(rack_json)
        appConfig.logger.debug(rack)
        print("Saw rack in message")
        appConfig.db.write_rack(rack)

    if 'recipe' in message:
        # a recipe is contained in this update
        entities_processed.append('recipe')
        recipe_json = message['recipe']
        recipe = Recipe.from_json(recipe_json)
        appConfig.logger.debug(recipe)
        print("Saw recipe in message")
        appConfig.db.write_recipe(recipe)

    if 'shelf' in message:
        # a shelf is contained in this update
        entities_processed.append('shelf')
        shelf_json = message['shelf']
        shelf = Shelf.from_json(shelf_json)
        appConfig.logger.debug(shelf)
        print("Saw shelf in message")
        appConfig.db.write_shelf(shelf)

    if 'plant' in message:
        # a plant is contained in this update
        entities_processed.append('plant')
        plant_json = message['plant']
        plant = Plant.from_json(plant_json)
        appConfig.logger.debug(plant)
        print("Saw plant in message")
        appConfig.db.write_plant(plant)


    emit('message_received', {'processed': entities_processed})



if __name__ == '__main__':
    socketio.run(app)
