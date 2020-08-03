import logging
from datetime import datetime, timedelta
from dateutil.parser import parse
from time import mktime

from typing import List, Optional

import grpc
from google.protobuf.timestamp_pb2 import Timestamp

from app.job_scheduler import helloworld_pb2
from app.job_scheduler import helloworld_pb2_grpc

from app.models.grow import Grow
from app.models.grow_phase import GrowPhase
from app.models.plant import Plant
from app.models.room import Room
from app.models.rack import Rack
from app.models.recipe import Recipe
from app.models.recipe_phase import RecipePhase
from app.models.shelf import Shelf
from app.models.shelf_grow import ShelfGrow

from app.resources.schedule_jobs import get_job_id
from app.resources.schedule_jobs import schedule_grow_for_shelf  # type: ignore

from app.utils.time_utils import iso8601_string_to_datetime

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

        send_message_to_namespace_if_specified(
            socketio, message, "message_received", {"processed": entities_processed}
        )

    @socketio.on("start_grows_for_shelves")
    def start_grows_for_shelves(message) -> None:
        print("message:", message)
        logging.debug("message sent to post_room_schedule:", message)
        if "grow_phases" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "start_grow_for_shelf_succeeded",
                {"succeeded": False, "reason": "Grow phases not included"},
            )
        elif "shelves" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "start_grow_for_shelf_succeeded",
                {"succeeded": False, "reason": "Shelves not included"},
            )
        elif "is_new_recipe" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "start_grow_for_shelf_succeeded",
                {
                    "succeeded": False,
                    "reason": "Not specified whether this is a new recipe",
                },
            )
        elif "end_date" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "start_grow_for_shelf_succeeded",
                {"succeeded": False, "reason": "End date not specified"},
            )

        is_new_recipe: bool = bool(message["is_new_recipe"])
        print("is_new_recipe:", is_new_recipe, message["is_new_recipe"])

        # TODO: Abstract this if/else statement into a method
        if is_new_recipe:
            # create the recipe and the recipe phases before creating the grow
            recipe_no_id: Recipe = Recipe(None, None)
            recipe: Recipe = app_config.db.write_recipe(recipe_no_id)

            recipe_phases: List[RecipePhase] = []
            for i in range(len(message["grow_phases"])):
                recipe_phase_json = message["grow_phases"][i]
                start_date: datetime = iso8601_string_to_datetime(
                    recipe_phase_json["start_date"]
                )

                # if this is the last phase, use `end_date` attribute
                is_last_phase = i == len(message["grow_phases"]) - 1
                end_date_str: str = message[
                    "end_date"
                ] if is_last_phase else recipe_phase_json["start_date"]
                end_date: datetime = iso8601_string_to_datetime(end_date_str)

                date_diff: timedelta = end_date - start_date
                # 60 seconds * 60 minutes = 3600 seconds in an hour
                num_hours: int = int(date_diff.total_seconds() / 3600)
                recipe_phase_json["num_hours"] = num_hours
                recipe_phase_json["recipe_phase_num"] = i
                recipe_phase_json["recipe_id"] = recipe.recipe_id

                recipe_phase: RecipePhase = RecipePhase.from_json(recipe_phase_json)
                recipe_phases.append(recipe_phase)

            print("recipe_phases:", recipe_phases)
            app_config.db.write_recipe_phases(recipe_phases)
        else:
            raise Exception(
                "Unsupported functionality of using an already existing recipe"
            )

        # create the grow first so we can read the grow_id
        grow_start_date: datetime = iso8601_string_to_datetime(
            message["grow_phases"][0]["start_date"]
        )
        grow_estimated_end_date: datetime = iso8601_string_to_datetime(
            message["end_date"]
        )
        grow_without_id: Grow = Grow(
            None, recipe.recipe_id, grow_start_date, grow_estimated_end_date
        )

        grow: Grow = app_config.db.write_grow(grow_without_id)

        grow_phases: List[GrowPhase] = []
        for i, gp in enumerate(message["grow_phases"]):
            gp["grow_id"] = grow.grow_id
            gp["phase_start_datetime"] = gp["start_date"]
            gp["recipe_id"] = recipe.recipe_id
            gp["recipe_phase_num"] = i
            if i == len(message["grow_phases"]) - 1:
                # this is the last phase, use `end_date` attribute
                gp["phase_end_datetime"] = message["end_date"]
                gp["is_last_phase"] = True
            else:
                gp["phase_end_datetime"] = message["grow_phases"][i + 1]["start_date"]
                gp["is_last_phase"] = False

            grow_phase = GrowPhase.from_json(gp)
            grow_phases.append(grow_phase)

        shelf_grows: List[ShelfGrow] = []
        for shelf_data in message["shelves"]:
            shelf_data["grow_id"] = grow.grow_id
            shelf_grow = ShelfGrow.from_json(shelf_data)
            shelf_grows.append(shelf_grow)

        # only schedule 1st grow phase, but write all grow phases to DB
        first_grow_phase: GrowPhase = grow_phases[0]
        (
            power_level,
            red_level,
            blue_level,
        ) = app_config.db.read_lights_from_recipe_phase(
            first_grow_phase.recipe_id, first_grow_phase.recipe_phase_num
        )

        if grow_phase.is_last_phase:
            # schedule this phase without an end date
            """
            app_config.scheduler.add_job(
                schedule_grow_for_shelf,
                "interval",
                start_date=first_grow_phase.phase_start_datetime,
                args=[shelf_grows, grow_phase, power_level, red_level, blue_level],
                id=get_job_id(shelf_grows, grow_phase),
                minutes=5,  # TODO: Put this in a constants file and link with usage in schedule_jobs.py
            )
            """
            with grpc.insecure_channel("sunrisa_job_scheduler:50051") as channel:
                stub = helloworld_pb2_grpc.GreeterStub(channel)
                shelf_grow_protos = [
                    helloworld_pb2.ShelfGrow(
                        grow_id=sg.grow_id,
                        room_id=sg.room_id,
                        rack_id=sg.rack_id,
                        shelf_id=sg.shelf_id,
                    )
                    for sg in shelf_grows
                ]

                phase_start_timestamp = Timestamp()
                phase_start_timestamp.FromDatetime(grow_phase.phase_start_datetime)

                phase_end_timestamp = Timestamp()
                phase_end_timestamp.FromDatetime(grow_phase.phase_end_datetime)

                grow_phase_proto = helloworld_pb2.GrowPhase(
                    grow_id=grow_phase.grow_id,
                    recipe_phase_num=grow_phase.recipe_phase_num,
                    recipe_id=grow_phase.recipe_id,
                    phase_start_datetime=phase_start_timestamp,
                    phase_end_datetime=phase_end_timestamp,
                    is_last_phase=grow_phase.is_last_phase,
                )
                proto = helloworld_pb2.HelloRequest(
                    name="LucasTest",
                    shelf_grows=shelf_grow_protos,
                    grow_phase=grow_phase_proto,
                    power_level=power_level,
                    red_level=red_level,
                    blue_level=blue_level,
                )
                response = stub.SayHello(proto)
            print("Greeter client received: " + response.message)
        else:
            """
            app_config.scheduler.add_job(
                schedule_grow_for_shelf,
                "interval",
                start_date=first_grow_phase.phase_start_datetime,
                end_date=first_grow_phase.phase_end_datetime,
                args=[shelf_grows, grow_phase, power_level, red_level, blue_level],
                id=get_job_id(shelf_grows, grow_phase),
                minutes=5,  # TODO: Put this in a constants file and link with usage in schedule_jobs.py
            )
            """
            with grpc.insecure_channel("sunrisa_job_scheduler:50051") as channel:
                stub = helloworld_pb2_grpc.GreeterStub(channel)
                response = stub.SayHello(helloworld_pb2.HelloRequest(name="wrong bitch"))
            print("Greeter client received: " + response.message)

        print("Didn't add job to scheduler")

        # write grow phases and shelf grows to db
        app_config.db.write_grow_phases(grow_phases)
        app_config.db.write_shelf_grows(shelf_grows)

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
        app_config.db.write_recipe(recipe)
        app_config.db.write_recipe_phases(recipe_phases)
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
        all_rooms: List[Room] = app_config.db.read_all_rooms()
        all_racks: List[Rack] = app_config.db.read_all_racks()
        all_shelves: List[Shelf] = app_config.db.read_all_shelves()
        all_current_grows: List[Grow] = app_config.db.read_current_grows()

        recipe_ids = {
            g.recipe_id for g in all_current_grows
        }  # use a set comprehension since grows may have duplicate recipes
        all_current_recipes: List[Recipe] = app_config.db.read_recipes(list(recipe_ids))

        all_grow_ids = [g.grow_id for g in all_current_grows]
        all_grow_phases: List[
            GrowPhase
        ] = app_config.db.read_grow_phases_from_multiple_grows(all_grow_ids)

        recipe_id_phase_num_pairs = [
            (g.recipe_id, g.recipe_phase_num) for g in all_grow_phases
        ]
        all_recipe_phases: List[RecipePhase] = app_config.db.read_recipe_phases(
            recipe_id_phase_num_pairs
        )

        all_current_shelf_grows: List[
            ShelfGrow
        ] = app_config.db.read_shelves_with_grows(all_grow_ids)

        entities_dict = {
            "rooms": [rm.to_json() for rm in all_rooms],
            "racks": [rck.to_json() for rck in all_racks],
            "shelves": [s.to_json() for s in all_shelves],
            "grows": [g.to_json() for g in all_current_grows],
            "grow_phases": [gp.to_json() for gp in all_grow_phases],
            "recipes": [r.to_json() for r in all_current_recipes],
            "recipe_phases": [rp.to_json() for rp in all_recipe_phases],
            "shelf_grows": [sg.to_json() for sg in all_current_shelf_grows],
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
