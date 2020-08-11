import logging
from datetime import datetime, timedelta
from dateutil.parser import parse
from time import mktime

from typing import Any, List, Optional

from app.job_scheduler.schedule_jobs import client_remove_job, client_reschedule_job, client_schedule_job

from app.models.grow import Grow
from app.models.grow_phase import GrowPhase
from app.models.plant import Plant
from app.models.room import Room
from app.models.rack import Rack
from app.models.recipe import Recipe
from app.models.recipe_phase import RecipePhase
from app.models.shelf import Shelf
from app.models.shelf_grow import ShelfGrow

from app.utils.grow_phase_utils import create_grow_phases_from_light_configurations, grow_phase_exists_with_phase_number, old_new_grow_phases_diff
from app.utils.recipe_phase_utils import create_recipe_phases_from_light_configurations, old_new_recipe_phases_diff, recipe_phase_exists_with_phase_number
from app.utils.time_utils import iso8601_string_to_datetime  # type: ignore

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
            print("Saw shelf in message", shelf)
            app_config.db.write_shelf(shelf)

        send_message_to_namespace_if_specified(
            socketio, message, "message_received", {"processed": entities_processed}
        )

    @socketio.on("modify_grow")
    def modify_grow(message) -> None:
        print("called modify_grow:", message)
        if "grow_id" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "modify_grow_response",
                {"succeeded": False, "reason": "Grow ID not included"},
            )
            return
        elif 'grow_phases' not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "modify_grow_response",
                {"succeeded": False, "reason": "Grow phases not included"},
            )
            return
        elif 'end_date' not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "modify_grow_response",
                {"succeeded": False, "reason": "End date not included"},
            )
            return
        elif 'recipe_name' not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "modify_grow_response",
                {"succeeded": False, "reason": "Recipe name not included"},
            )
            return
        
        grow_id: int = message["grow_id"]
        grow: Optional[Grow] = app_config.db.read_grow(grow_id)
        if not grow:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "modify_grow_response",
                {"succeeded": False, "reason": "Grow not found"},
            )
            return

        old_grow_phases: List[GrowPhase] = app_config.db.read_grow_phases(grow_id)
        if not old_grow_phases:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "modify_grow_response",
                {"succeeded": False, "reason": "Previous grow phases not found"},
            )
            return

        old_recipe_phases: List[RecipePhase] = app_config.db.read_phases_from_recipe(grow.recipe_id)
        if not old_recipe_phases:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "modify_grow_response",
                {"succeeded": False, "reason": "Previous recipe phases not found"},
            )
            return
        
        light_configurations: List[Any] = message["grow_phases"]
        end_date_str: str = message["end_date"]
        end_date: datetime = iso8601_string_to_datetime(end_date_str)
        recipe_id: int = grow.recipe_id

        # first update the grow phases, because the grow phases depend on the recipe phases (and you can't delete a
        # recipe phase that has a grow phase as a foreign key relation)
        new_grow_phases: List[GrowPhase] = create_grow_phases_from_light_configurations(light_configurations, grow_id, recipe_id, end_date)

        grow_phases_added, grow_phases_removed, grow_phases_modified = old_new_grow_phases_diff(old_grow_phases, new_grow_phases)
        print("grow phases added:", grow_phases_added)
        print("grow phases removed:", grow_phases_removed)
        print("grow phases modified:", grow_phases_modified)

        if grow_phases_added or grow_phases_modified or grow_phases_removed:
            # need to edit grow phases. Keep it simple and delete all old ones, then re-create all new
            # phases.
            app_config.db.delete_grow_phases_from_grow(grow.grow_id)
            app_config.db.write_grow_phases(new_grow_phases)

        # now update recipe phases
        new_recipe_phases: List[RecipePhase] = create_recipe_phases_from_light_configurations(light_configurations, grow.recipe_id, end_date)
        recipe_phases_added, recipe_phases_removed, recipe_phases_modified = old_new_recipe_phases_diff(old_recipe_phases, new_recipe_phases)

        print("recipe phases added:", recipe_phases_added)
        print("recipe phases removed:", recipe_phases_removed)
        print("recipe phases modified:", recipe_phases_modified)

        if recipe_phases_added or recipe_phases_removed or recipe_phases_modified:
            # if this is a new recipe, we can update the recipe phases. Else, we need to create a new recipe
            # and associate it with the grow.
            if grow.is_new_recipe:
                # this is a new recipe, update the recipe phases by deleting and re-creating.
                app_config.db.delete_recipe_phases_from_recipe(grow.recipe_id)
                app_config.db.write_recipe_phases(new_recipe_phases)
            else:
                # this is not a new recipe, we don't want to change the template recipe. Create a new recipe that has
                # the edits.
                new_recipe_name: str = message["recipe_name"]
                new_recipe_no_id: Recipe = Recipe(None, new_recipe_name)
                new_recipe: Recipe = app_config.db.write_recipe(new_recipe_no_id)

                # update recipe phases and grow to have the new recipe_id
                recipe_phases: List[RecipePhase] = []
                for recipe_phase in new_recipe_phases:
                    recipe_phase.recipe_id = new_recipe.recipe_id
                    recipe_phases.append(recipe_phase)
                
                app_config.db.write_recipe_phases(recipe_phases)
                app_config.db.update_grow_recipe(grow.grow_id, new_recipe.recipe_id)
            

        # you can't modify current running phase in job scheduler, but you could change the start time
        # of the phase directly afterwards. Check if the phase after the current phase was modified or deleted,
        # if modified we need to change the jobs end date to the new phases start date, if deleted need to make 
        # the current job run forever. We can handle this easily by deleting the current job and rescheduling it
        # with the current phase (which should have updated start and end dates).
        next_phase: int = grow.current_phase + 1

        was_next_grow_phase_modified: bool = grow_phase_exists_with_phase_number(next_phase, grow_phases_modified)
        was_next_grow_phase_removed: bool = grow_phase_exists_with_phase_number(next_phase, grow_phases_removed)
        was_next_recipe_phase_modified: bool = recipe_phase_exists_with_phase_number(next_phase, recipe_phases_modified)
        was_next_recipe_phase_removed: bool = recipe_phase_exists_with_phase_number(next_phase, recipe_phases_removed)

        if was_next_grow_phase_modified or was_next_grow_phase_removed or was_next_recipe_phase_modified or was_next_recipe_phase_removed:
            # next grow phase or next recipe phase was modified or removed, reschedule the job that is currently running
            grow_phase = new_grow_phases[grow.current_phase]
            client_reschedule_job(app_config, grow_phase)
        
        # change the grows start and end dates if they were modified
        new_start_datetime: datetime = new_grow_phases[0].phase_start_datetime
        new_estimated_end_datetime: datetime = new_grow_phases[-1].phase_end_datetime

        if grow.start_datetime != new_start_datetime or grow.estimated_end_datetime != new_estimated_end_datetime:
            app_config.db.update_grow_dates(grow.grow_id, new_start_datetime, new_estimated_end_datetime)    
        
        send_message_to_namespace_if_specified(
            socketio,
            message,
            "modify_grow_response",
            {"succeeded": True},
        )

    @socketio.on("read_grow_with_phases")
    def read_grow_with_phases(message) -> None:
        print("called read_grow_with_phases")
        if "grow" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "read_grow_with_phases_response",
                {"succeeded": False, "reason": "Grow not included"},
            )
            return

        grow_json = message["grow"]
        grow_id: int = int(grow_json["grow_id"])
        grow: Optional[Grow] = app_config.db.read_grow(grow_id)
        if not grow:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "read_grow_with_phases_response",
                {"succeeded": False, "reason": "Grow not found"},
            )
            return

        grow_phases: List[GrowPhase] = app_config.db.read_grow_phases(grow_id)
        if not grow_phases:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "read_grow_with_phases_response",
                {"succeeded": False, "reason": "Grow not found"},
            )
            return

        recipe: Optional[Recipe] = app_config.db.read_recipe(grow.recipe_id)
        if not recipe:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "read_grow_with_phases_response",
                {"succeeded": False, "reason": "Recipe not found"},
            )
            return

        recipe_phases: List[RecipePhase] = app_config.db.read_phases_from_recipe(
            grow.recipe_id
        )
        if not recipe_phases:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "read_grow_with_phases_response",
                {"succeeded": False, "reason": "Recipe phases not found"},
            )
            return

        send_message_to_namespace_if_specified(
            socketio,
            message,
            "read_grow_with_phases_response",
            {
                "succeeded": True,
                "grow": grow.to_json(),
                "grow_phases": [gp.to_json() for gp in grow_phases],
                "recipe_phases": [rp.to_json() for rp in recipe_phases],
                "recipe": recipe.to_json(),
            },
        )

    @socketio.on("read_grow")
    def read_grow(message) -> None:
        print("called read_grow")
        if "grow" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "read_grow_response",
                {"succeeded": False, "reason": "Grow not included"},
            )
            return

        grow_json = message["grow"]
        grow_id: int = int(grow_json["grow_id"])
        grow: Optional[Grow] = app_config.db.read_grow(grow_id)
        if not grow:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "read_grow_response",
                {"succeeded": False, "reason": "Grow not found"},
            )
            return

        send_message_to_namespace_if_specified(
            socketio,
            message,
            "read_grow_response",
            {"succeeded": True, "grow": grow.to_json()},
        )

    @socketio.on("search_recipes")
    def search_recipes(message) -> None:
        print("search_recipes message:", message)
        if "search_name" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "search_recipes_response",
                {"succeeded": False, "reason": "Search name not included"},
            )
            return

        search_name: str = message["search_name"]
        matching_recipes: List[Recipe] = app_config.db.read_recipes_with_name(
            search_name
        )

        recipe_ids: List[int] = [r.recipe_id for r in matching_recipes]
        recipe_phases: List[RecipePhase] = app_config.db.read_phases_from_recipes(
            recipe_ids
        )

        recipes_json = [r.to_json() for r in matching_recipes]
        recipe_phases_json = [rp.to_json() for rp in recipe_phases]

        send_message_to_namespace_if_specified(
            socketio,
            message,
            "search_recipes_response",
            {
                "succeeded": True,
                "recipes": recipes_json,
                "recipe_phases": recipe_phases_json,
            },
        )

    @socketio.on("harvest_grow")
    def harvest_grow(message) -> None:
        print("message:", message)
        if "grow" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "harvest_grow_response",
                {"succeeded": False, "reason": "Grow not included"},
            )
            return

        grow_json = message["grow"]
        grow_id: int = int(grow_json["grow_id"])
        grow: Optional[Grow] = app_config.db.read_grow(grow_id)
        if not grow:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "harvest_grow_response",
                {"succeeded": False, "reason": "Grow not found"},
            )
            return

        found_grow_json = grow.to_json()
        # read all data sent in by user, and mark it on grow
        for key in grow_json:
            found_grow_json[key] = grow_json[key]

        updated_grow: Grow = Grow.from_json(found_grow_json)

        # harvest the grow by marking it as complete
        harvest_datetime: datetime = datetime.utcnow()
        updated_grow.estimated_end_datetime = harvest_datetime
        updated_grow.is_finished = True

        print("grow_json to harvest:", grow_json, flush=True)
        # end grow
        app_config.db.harvest_grow(updated_grow)

        # read current grow phase
        current_phase: int = updated_grow.current_phase
        current_grow_phase: Optional[GrowPhase] = app_config.db.read_grow_phase(
            updated_grow.grow_id, current_phase
        )
        if not current_grow_phase:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "harvest_grow_response",
                {
                    "succeeded": False,
                    "reason": "Current grow phase {} not found".format(current_phase),
                },
            )
            return

        # remove ongoing job so that it stops running
        client_remove_job(current_grow_phase)

        # update last recipe phase to have proper end date
        print("Updating grow_phase:", current_grow_phase)
        app_config.db.end_grow_phase(current_grow_phase, harvest_datetime)
        send_message_to_namespace_if_specified(
            socketio, message, "harvest_grow_response", {"succeeded": True},
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
            return
        elif "shelves" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "start_grow_for_shelf_succeeded",
                {"succeeded": False, "reason": "Shelves not included"},
            )
            return
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
            return
        elif "end_date" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "start_grow_for_shelf_succeeded",
                {"succeeded": False, "reason": "End date not specified"},
            )
            return

        is_new_recipe: bool = bool(message["is_new_recipe"])
        print("is_new_recipe:", is_new_recipe, message["is_new_recipe"])

        if is_new_recipe:
            # create the recipe and the recipe phases before creating the grow
            recipe_name = message["recipe_name"] if "recipe_name" in message else None
            recipe_no_id: Recipe = Recipe(None, recipe_name)
            recipe: Recipe = app_config.db.write_recipe(recipe_no_id)
            recipe_id: int = recipe.recipe_id

            light_configurations: List[Any] = message["grow_phases"]
            end_date_str: str = message["end_date"]
            end_date: datetime = iso8601_string_to_datetime(end_date_str)

            recipe_phases: List[RecipePhase] = create_recipe_phases_from_light_configurations(light_configurations, recipe_id, end_date)
            print("recipe_phases:", recipe_phases)
            # write the recipe phases to database
            app_config.db.write_recipe_phases(recipe_phases)

        else:
            recipe_id: int = message["template_recipe_id"]

        # create the grow first so we can read the grow_id
        grow_start_date: datetime = iso8601_string_to_datetime(
            message["grow_phases"][0]["start_date"]
        )
        grow_estimated_end_date: datetime = iso8601_string_to_datetime(
            message["end_date"]
        )

        current_phase: int = 0
        grow_without_id: Grow = Grow(
            None,
            recipe_id,
            grow_start_date,
            grow_estimated_end_date,
            False,
            False,
            None,
            current_phase,
            is_new_recipe,
        )

        grow: Grow = app_config.db.write_grow(grow_without_id)

        light_configurations = message["grow_phases"]
        end_date_str: str = message["end_date"]
        end_date: datetime = iso8601_string_to_datetime(end_date_str)
        grow_phases: List[GrowPhase] = create_grow_phases_from_light_configurations(light_configurations, grow.grow_id, recipe_id, end_date)

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

        # enqueue the job to the job scheduler
        client_schedule_job(
            shelf_grows, first_grow_phase, power_level, red_level, blue_level
        )

        # write grow phases and shelf grows to db
        app_config.db.write_grow_phases(grow_phases)
        app_config.db.write_shelf_grows(shelf_grows)

        logging.debug("start_grow_for_shelf succeeded!")
        send_message_to_namespace_if_specified(
            socketio,
            message,
            "start_grows_for_shelves_succeeded",
            {"succeeded": True, "grow": grow.to_json()},
        )
        print("Grow started successfully, event emitted")

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
