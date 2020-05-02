import logging

from typing import Optional

from app.models.room import Room
from app.models.rack import Rack
from app.models.recipe import Recipe
from app.models.shelf import Shelf
from app.models.plant import Plant


def init_event_listeners(app_config, socketio):
    @socketio.on("connect")
    def connect():
        print("I'm connected!")

    @socketio.on("connect_error")
    def connect_error():
        print("The connection failed!")

    @socketio.on("disconnect")
    def disconnect():
        print("I'm disconnected!")

    @socketio.on("message_sent")
    def log_changes(message):
        logging.debug("message sent:", message)
        entities_processed = []

        print("message:", message)
        if "room" in message:
            # a room is contained in this update
            entities_processed.append("room")
            room_json = message["room"]
            room = Room.from_json(room_json)
            app_config.logger.debug(room)
            print("Saw room in message")
            app_config.db.write_room(room)

        if "rack" in message:
            # a rack is contained in this update
            entities_processed.append("rack")
            rack_json = message["rack"]
            rack = Rack.from_json(rack_json)
            app_config.logger.debug(rack)
            print("Saw rack in message")
            app_config.db.write_rack(rack)

        if "recipe" in message:
            # a recipe is contained in this update
            entities_processed.append("recipe")
            recipe_json = message["recipe"]
            recipe = Recipe.from_json(recipe_json)
            app_config.logger.debug(recipe)
            print("Saw recipe in message")
            app_config.db.write_recipe(recipe)

        if "shelf" in message:
            # a shelf is contained in this update
            entities_processed.append("shelf")
            shelf_json = message["shelf"]
            shelf = Shelf.from_json(shelf_json)
            app_config.logger.debug(shelf)
            print("Saw shelf in message")
            app_config.db.write_shelf(shelf)

        if "plant" in message:
            # a plant is contained in this update
            entities_processed.append("plant")
            plant_json = message["plant"]
            plant = Plant.from_json(plant_json)
            app_config.logger.debug(plant)
            print("Saw plant in message")
            app_config.db.write_plant(plant)

        socketio.emit("message_received", {"processed": entities_processed})


    @socketio.on("read_all_rooms")
    def read_all_rooms(message) -> None:
        all_rooms = app_config.db.read_all_rooms()

        rooms = [room.to_json() for room in all_rooms]
        print("rooms:", rooms)
        socketio.emit("return_rooms", {"rooms": rooms})


    @socketio.on("read_room")
    def read_room(message) -> None:
        room: Optional[Room] = None
        if "room" in message:
            room_id = message["room"]["room_id"]
            room = app_config.db.read_room(room_id)

        socketio.emit("return_room", {"room": room.to_json() if room else None})
