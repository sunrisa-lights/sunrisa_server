import logging
from datetime import datetime
from dateutil.parser import parse
from time import mktime

from typing import List, Optional

from app.models.grow import Grow
from app.models.plant import Plant
from app.models.room import Room
from app.models.rack import Rack
from app.models.recipe import Recipe
from app.models.recipe_phase import RecipePhase
from app.models.shelf import Shelf

from app.resources.schedule_jobs import schedule_grow_for_shelf  # type: ignore

NAMESPACE = "namespace"


def send_message_to_namespace_if_specified(socketio, message, event_name, event_data):
    if NAMESPACE in message:
        message_namespace = message[NAMESPACE]
        print("Emitting event with namespace:", message_namespace)
        socketio.emit(event_name, event_data, namespace=message_namespace)
    else:
        socketio.emit(event_name, event_data)


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
    def message_sent(message):
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

        send_message_to_namespace_if_specified(
            socketio, message, "message_received", {"processed": entities_processed}
        )

    @socketio.on("start_grows_for_shelves")
    def start_grows_for_shelves(message) -> None:
        print("message:", message)
        logging.debug("message sent to post_room_schedule:", message)
        if "grows" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "start_grow_for_shelf_succeeded",
                {"succeeded": False, "reason": "Grow not included"},
            )

        grows: List[Grow] = [Grow.from_json(g) for g in message["grows"]]

        for grow in grows:
            (
                power_level,
                red_level,
                blue_level,
            ) = app_config.db.read_lights_from_recipe_phase(
                grow.recipe_id, grow.recipe_phase_num
            )

            app_config.scheduler.add_job(
                schedule_grow_for_shelf,
                "interval",
                start_date=grow.start_datetime,
                end_date=grow.end_datetime,
                args=[grow, power_level, red_level, blue_level],
                id=grow.to_job_id(),
                minutes=5,
            )

        # TODO (lww515): What to do after harvest is finished?

        # write grows to db
        app_config.db.write_grows(grows)

        logging.debug("start_grow_for_shelf succeeded!")
        send_message_to_namespace_if_specified(
            socketio, message, "start_grows_for_shelves_succeeded", {"succeeded": True}
        )
        print("Grow started successfully, event emitted")

    @socketio.on("get_current_shelf_grows")
    def get_current_shelf_grows(message) -> None:
        print("get_current_shelf_grows called with message:", message)
        if "shelf" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "get_current_shelf_schedules_response",
                {"succeeded": False, "reason": "Shelf ID missing",},
            )
        print("Returned get_current_shelf_schedules_succeeded")

        shelf_dict = message["shelf"]
        shelf_id = shelf_dict["shelf_id"]

        current_grows: List[Grow] = app_config.db.read_current_shelf_grows(shelf_id)
        shelf_grow_json = [grow.to_json() for grow in current_grows]
        send_message_to_namespace_if_specified(
            socketio,
            message,
            "get_current_shelf_schedules_response",
            {"succeeded": True, "current_shelf_grows": shelf_grow_json},
        )
        print("Returned get_current_shelf_grows_succeeded2")

    @socketio.on("create_new_recipe")
    def create_new_recipe(message) -> None:
        if "recipe" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "create_new_recipe_response",
                {"succeeded": False, "reason": "no recipe"},
            )
        elif "recipe_phases" not in message["recipe"]:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "create_new_recipe_response",
                {"succeeded": False, "reason": "no recipe phases"},
            )

        recipe_json = message["recipe"]
        recipe = Recipe.from_json(recipe_json)

        recipe_phases: List[RecipePhase] = []

        json_recipe_phases = recipe_json["recipe_phases"]
        for rpl in json_recipe_phases:
            recipe_phase = RecipePhase.from_json(rpl)
            recipe_phases.append(recipe_phase)

        app_config.logger.debug(recipe)
        app_config.logger.debug(recipe_phases)

        print("Saw recipe in message")
        app_config.db.write_recipe_with_phases(recipe, recipe_phases)
        print("CREATED RECIPE WITH PHASES")
        send_message_to_namespace_if_specified(
            socketio, message, "create_new_recipe_response", {"succeeded": True}
        )

    @socketio.on("read_all_rooms")
    def read_all_rooms(message) -> None:
        all_rooms = app_config.db.read_all_rooms()

        rooms = [room.to_json() for room in all_rooms]
        app_config.logger.debug("rooms: {}".format(rooms))
        print("rooms:", rooms)
        send_message_to_namespace_if_specified(
            socketio, message, "return_rooms", {"rooms": rooms}
        )

    @socketio.on("read_all_racks_in_room")
    def read_all_racks_in_room(message) -> None:
        all_racks_in_room = []
        if "room" in message:
            room_id = int(message["room"]["room_id"])
            racks = app_config.db.read_racks_in_room(room_id)
            all_racks_in_room = [r.to_json() for r in racks]

        app_config.logger.debug(
            "room_id: {}, racks: {}".format(room_id, all_racks_in_room)
        )
        send_message_to_namespace_if_specified(
            socketio,
            message,
            "return_racks_in_room",
            {"racks": all_racks_in_room, "room_id": room_id},
        )

    @socketio.on("read_all_entities")
    def read_all_entities(message) -> None:
        print("read_all_entities event emitted")
        all_rooms = app_config.db.read_all_rooms()
        all_racks = app_config.db.read_all_racks()
        all_shelves = app_config.db.read_all_shelves()
        all_current_grows = app_config.db.read_current_grows()

        recipe_ids = {
            g.recipe_id for g in all_current_grows
        }  # use a set comprehension since grows may have duplicate recipes
        all_current_recipes = app_config.db.read_recipes(list(recipe_ids))

        recipe_id_phase_num_pairs = [
            (g.recipe_id, g.recipe_phase_num) for g in all_current_grows
        ]
        all_current_recipe_phases = app_config.db.read_recipe_phases(
            recipe_id_phase_num_pairs
        )

        entities_dict = {
            "rooms": [rm.to_json() for rm in all_rooms],
            "racks": [rck.to_json() for rck in all_racks],
            "shelves": [s.to_json() for s in all_shelves],
            "grows": [g.to_json() for g in all_current_grows],
            "recipes": [r.to_json() for r in all_current_recipes],
            "recipe_phases": [rp.to_json() for rp in all_current_recipe_phases],
        }

        app_config.logger.debug("returning entities: {}".format(entities_dict))
        print("Returning entities:", entities_dict)
        send_message_to_namespace_if_specified(
            socketio, message, "return_all_entities", entities_dict
        )

    @socketio.on("read_room")
    def read_room(message) -> None:
        room: Optional[Room] = None
        print("message:", message)
        if "room" in message:
            room_id = message["room"]["room_id"]
            # room is None if not found
            room = app_config.db.read_room(room_id)
            print("Queried for room:", room)

        print("found_room:", room)
        send_message_to_namespace_if_specified(
            socketio, message, "return_room", {"room": room.to_json() if room else None}
        )
