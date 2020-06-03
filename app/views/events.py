import logging
from datetime import datetime

from typing import Optional

from app.models.room import Room
from app.models.rack import Rack
from app.models.recipe import Recipe
from app.models.shelf import Shelf
from app.models.plant import Plant

from app.resources.schedule_jobs import schedule_job_for_room


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

        if "schedule" in message:
            # a schedule is contained in this update
            entities_processed.append("schedule")
            schedule_json = message["schedule"]
            app_config.logger.debug(schedule_json)
            print("Saw schedule in message")
            shelf_id = int(schedule_json['shelf_id'])
            start_time = schedule_json['start_time']
            end_time = schedule_json['end_time']
            power_level = schedule_json['power_level']
            red_level = schedule_json['red_level']
            blue_level = schedule_json['blue_level']
            app_config.db.write_schedule_for_shelf(shelf_id, start_time, end_time, power_level, red_level, blue_level)

        socketio.emit("message_received", {"processed": entities_processed})

    @socketio.on("post_room_schedule")
    def post_room_schedule(message) -> None:
        schedule_json = message["schedule"]
        app_config.logger.debug(schedule_json)
        room_id = int(schedule_json['room_id'])
        start_time = schedule_json['start_time']
        end_time = schedule_json['end_time']
        power_level = schedule_json['power_level']
        red_level = schedule_json['red_level']
        blue_level = schedule_json['blue_level']

        start_datetime = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

        app_config.scheduler.add_job(schedule_job_for_room, 'date', run_date=start_datetime, args=[socketio, room_id, power_level, red_level, blue_level])
        app_config.scheduler.add_job(schedule_job_for_room, 'date', run_date=end_datetime, args=[socketio, room_id, 0, 0, 0]) # assume we turn off the room after the job is done
        # write room schedule to db
        app_config.db.write_schedule_for_shelf(room_id, start_time, end_time, power_level, red_level, blue_level)

    @socketio.on("read_all_rooms")
    def read_all_rooms(message) -> None:
        all_rooms = app_config.db.read_all_rooms()

        rooms = [room.to_json() for room in all_rooms]
        app_config.logger.debug("rooms: {}".format(rooms))
        print("rooms:", rooms)
        socketio.emit("return_rooms", {"rooms": rooms})

    @socketio.on("read_all_racks_in_room")
    def read_all_racks_in_room(message) -> None:
        all_racks_in_room = []
        if 'room' in message:
            room_id = int(message['room']['room_id'])
            racks = app_config.db.read_racks_in_room(room_id)
            all_racks_in_room = [r.to_json() for r in racks]

        app_config.logger.debug("room_id: {}, racks: {}".format(room_id, all_racks_in_room))
        socketio.emit("return_racks_in_room", {"racks": all_racks_in_room, 'room_id': room_id})


    @socketio.on("read_all_entities")
    def read_all_entities(message) -> None:
        print("read_all_entities event emitted")
        all_entities = []
        all_rooms = app_config.db.read_all_rooms()
        for room in all_rooms:
            racks = app_config.db.read_racks_in_room(room.room_id)
            all_racks_in_room = [rack.to_json() for rack in racks]
            room_json = room.to_json()
            room_json['racks'] = all_racks_in_room
            all_entities.append(room_json)

        app_config.logger.debug("returning entities: {}".format(all_entities))
        print("Returning entities:", all_entities)
        socketio.emit("return_all_entities", {"rooms": all_entities})

    @socketio.on("read_room")
    def read_room(message) -> None:
        room: Optional[Room] = None
        if "room" in message:
            room_id = message["room"]["room_id"]
            # room is None if not found
            room = app_config.db.read_room(room_id)

        socketio.emit("return_room", {"room": room.to_json() if room else None})
