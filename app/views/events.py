import logging
from datetime import datetime, timedelta
from dateutil.parser import parse
from time import mktime
import json

from typing import Any, List, Optional

from app.job_scheduler.schedule_jobs import (
    client_remove_job,
    client_reschedule_job,
    client_schedule_job,
)

from app.models.grow import Grow
from app.models.grow_phase import GrowPhase
from app.models.plant import Plant
from app.models.room import Room
from app.models.rack import Rack
from app.models.recipe import Recipe
from app.models.recipe_phase import RecipePhase
from app.models.shelf import Shelf
from app.models.shelf_grow import ShelfGrow

from app.utils.grow_phase_utils import (
    create_grow_phases_from_light_configurations,
    grow_phase_exists_with_phase_number,
    old_new_grow_phases_diff,
)
from app.utils.recipe_phase_utils import (
    create_recipe_phases_from_light_configurations,
    old_new_recipe_phases_diff,
    recipe_phase_exists_with_phase_number,
)
from app.utils.time_utils import iso8601_string_to_datetime  # type: ignore

from app.validation.start_grows_for_shelves import (
    validate_start_grows_for_shelves,
)

from app.views.constants import NAMESPACE


def send_message_to_namespace_if_specified(
    socketio, message, event_name, event_data
):
    if NAMESPACE in message:
        message_namespace = message[NAMESPACE]
        socketio.emit(
            event_name, json.dumps(event_data), namespace=message_namespace
        )
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

    @socketio.on("create_object")
    def create_object(message):
        entities_processed = []

        print("received message:", message)
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
            socketio,
            message,
            "create_object_success",
            {"processed": entities_processed},
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
        elif "grow_phases" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "modify_grow_response",
                {"succeeded": False, "reason": "Grow phases not included"},
            )
            return
        elif "end_date" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "modify_grow_response",
                {"succeeded": False, "reason": "End date not included"},
            )
            return
        elif "recipe_name" not in message:
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

        old_grow_phases: List[GrowPhase] = app_config.db.read_grow_phases(
            grow_id
        )
        if not old_grow_phases:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "modify_grow_response",
                {
                    "succeeded": False,
                    "reason": "Previous grow phases not found",
                },
            )
            return

        recipe: Optional[Recipe] = app_config.db.read_recipe(grow.recipe_id)
        if not recipe:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "modify_grow_response",
                {"succeeded": False, "reason": "Recipe not found"},
            )
            return

        old_recipe_phases: List[
            RecipePhase
        ] = app_config.db.read_phases_from_recipe(grow.recipe_id)
        if not old_recipe_phases:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "modify_grow_response",
                {
                    "succeeded": False,
                    "reason": "Previous recipe phases not found",
                },
            )
            return

        light_configurations: List[Any] = message["grow_phases"]
        end_date_str: str = message["end_date"]
        end_date: datetime = iso8601_string_to_datetime(end_date_str)
        if not grow.recipe_id:
            raise ValueError("recipe_id doesn't exist on grow")
            return
        else:
            recipe_id: int = grow.recipe_id

        new_grow_phases: List[
            GrowPhase
        ] = create_grow_phases_from_light_configurations(
            light_configurations, grow_id, recipe_id, end_date
        )

        grow_phases_added, grow_phases_removed, grow_phases_modified = old_new_grow_phases_diff(
            old_grow_phases, new_grow_phases
        )
        print("grow phases added:", grow_phases_added)
        print("grow phases removed:", grow_phases_removed)
        print("grow phases modified:", grow_phases_modified)

        new_recipe_phases: List[
            RecipePhase
        ] = create_recipe_phases_from_light_configurations(
            light_configurations, grow.recipe_id, end_date
        )
        recipe_phases_added, recipe_phases_removed, recipe_phases_modified = old_new_recipe_phases_diff(
            old_recipe_phases, new_recipe_phases
        )

        print("recipe phases added:", recipe_phases_added)
        print("recipe phases removed:", recipe_phases_removed)
        print("recipe phases modified:", recipe_phases_modified)

        grow_phase_edits_needed: bool = grow_phases_added or grow_phases_modified or grow_phases_removed

        if grow_phase_edits_needed:
            # need to edit grow phases. Keep it simple and delete all old ones, then re-create all new
            # phases. We can only delete here because grow phases rely on recipe phases for foreign key relations,
            # and we cannot create the grow phases yet because they will depend on the recipe phases being created.
            # Therefore we will create the grow phases after the recipe phase logic is executed.
            app_config.db.delete_grow_phases_from_grow(grow.grow_id)

        recipe_phase_edits_needed: bool = recipe_phases_added or recipe_phases_removed or recipe_phases_modified

        if recipe_phase_edits_needed:
            # if this is a new recipe, we can update the recipe phases. Else, we need to create a new recipe
            # and associate it with the grow.
            if grow.is_new_recipe:
                # this is a new recipe, update the recipe phases. We can't delete and re-create the recipe
                # phases since the grow phases have foreign key relations on them.
                app_config.db.delete_recipe_phases(recipe_phases_removed)
                app_config.db.update_recipe_phases(recipe_phases_modified)
                app_config.db.write_recipe_phases(recipe_phases_added)
            else:
                # this is not a new recipe, we don't want to change the template recipe. Create a new recipe that has
                # the edits.
                new_recipe_name: str = message["recipe_name"]
                new_recipe_no_id: Recipe = Recipe(None, new_recipe_name)
                new_recipe: Recipe = app_config.db.write_recipe(
                    new_recipe_no_id
                )

                # update recipe phases, grow and grow phases to have the new recipe_id
                recipe_phases: List[RecipePhase] = []
                for recipe_phase in new_recipe_phases:
                    if not new_recipe.recipe_id:
                        raise ValueError("No recipe ID in new_recipe_phases")
                    else:
                        recipe_phase.recipe_id = new_recipe.recipe_id
                    recipe_phases.append(recipe_phase)

                app_config.db.write_recipe_phases(recipe_phases)
                app_config.db.update_grow_recipe(
                    grow.grow_id, new_recipe.recipe_id
                )
                if not grow_phase_edits_needed:
                    # grow phases never got deleted, so we can update the recipe on the grow phases.
                    # if they got deleted, will batch in the recipe phase update with the grow phase creation.
                    app_config.db.update_grow_phases_recipe_from_grow(
                        grow.grow_id, new_recipe.recipe_id
                    )

        was_new_recipe_created: bool = recipe_phase_edits_needed and not grow.is_new_recipe

        if grow_phase_edits_needed:
            if was_new_recipe_created:
                # a new recipe was created. Update the grows recipe, and update the grow phases recipe as well.
                for gp in new_grow_phases:
                    if not new_recipe.recipe_id:
                        raise ValueError("No recipe ID in new_grow_phases")
                    else:
                        gp.recipe_id = new_recipe.recipe_id

            # we deleted the previous grow phases, now we recreate them. We recreate them after
            # the recipe phases are created because grow phases have a foreign key relation with recipe phases.
            app_config.db.write_grow_phases(new_grow_phases)

        recipe_name: str = message["recipe_name"]
        if recipe_name != recipe.recipe_name and not was_new_recipe_created:
            # if the recipe_name is different and a new recipe wasn't created with the recipe_name, then
            # update the current recipe
            recipe.recipe_name = recipe_name
            app_config.db.update_recipe_name(recipe)

        # you can't modify current running phase in job scheduler, but you could change the start time
        # of the phase directly afterwards. Check if the phase after the current phase was modified, deleted or added,
        # if modified we need to change the jobs end date to the new phases start date, if deleted need to make
        # the current job run forever, if added we need to reschedule the current job with an end date. We can handle
        # this easily by deleting the current job and rescheduling it with the current phase (which should have updated start and end dates).
        # because you can't modify the current phase, we only care about dates and not light values, so we only check the grow phases.
        next_phase: int = grow.current_phase + 1

        was_next_grow_phase_modified: bool = grow_phase_exists_with_phase_number(
            next_phase, grow_phases_modified
        )
        was_next_grow_phase_removed: bool = grow_phase_exists_with_phase_number(
            next_phase, grow_phases_removed
        )
        was_next_grow_phase_added: bool = grow_phase_exists_with_phase_number(
            next_phase, grow_phases_added
        )

        if (
            was_next_grow_phase_modified
            or was_next_grow_phase_removed
            or was_next_grow_phase_added
        ):
            # next grow phase was added/modified/removed, reschedule the job that is currently running
            # use the old grow phase to delete the current job, then add the new grow phase in.
            old_grow_phase: GrowPhase = old_grow_phases[grow.current_phase]
            new_grow_phase: GrowPhase = new_grow_phases[grow.current_phase]
            client_reschedule_job(app_config, old_grow_phase, new_grow_phase)

        # change the grows start and end dates if they were modified
        new_start_datetime: datetime = new_grow_phases[0].phase_start_datetime
        new_estimated_end_datetime: datetime = new_grow_phases[
            -1
        ].phase_end_datetime

        if (
            grow.start_datetime != new_start_datetime
            or grow.estimated_end_datetime != new_estimated_end_datetime
        ):
            app_config.db.update_grow_dates(
                grow.grow_id, new_start_datetime, new_estimated_end_datetime
            )

        send_message_to_namespace_if_specified(
            socketio, message, "modify_grow_response", {"succeeded": True}
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

        recipe_phases: List[
            RecipePhase
        ] = app_config.db.read_phases_from_recipe(grow.recipe_id)
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
        recipe_ids: List[int] = []
        for r in matching_recipes:
            if not r.recipe_id:
                raise ValueError("recipe_id null on recipe {}".format(r))
            else:
                recipe_ids.append(r.recipe_id)

        recipe_phases: List[
            RecipePhase
        ] = app_config.db.read_phases_from_recipes(recipe_ids)

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

    @socketio.on("update_incomplete_grow")
    def update_incomplete_grow(message) -> None:
        print("message:", message)
        if "grow" not in message:
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "update_incomplete_grow_response",
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
                "update_incomplete_grow_response",
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
        print(
            "grow_json to harvest in update_incomplete_grow:",
            grow_json,
            updated_grow,
            flush=True,
        )
        # end grow
        app_config.db.update_grow_harvest_data(updated_grow)

        send_message_to_namespace_if_specified(
            socketio,
            message,
            "update_incomplete_grow_response",
            {"succeeded": True},
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
        app_config.db.update_grow_harvest_data(updated_grow)

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
                    "reason": "Current grow phase {} not found".format(
                        current_phase
                    ),
                },
            )
            return

        # remove ongoing job so that it stops running
        client_remove_job(current_grow_phase)

        # update last recipe phase to have proper end date
        print("Updating grow_phase:", current_grow_phase)
        app_config.db.end_grow_phase(current_grow_phase, harvest_datetime)
        send_message_to_namespace_if_specified(
            socketio, message, "harvest_grow_response", {"succeeded": True}
        )

    @socketio.on("start_grows_for_shelves")
    def start_grows_for_shelves(message) -> None:
        try:
            validation_succeeded, failure_reason = validate_start_grows_for_shelves(
                app_config, message
            )
            print(
                "Start_grows_for_shelves validation:",
                validation_succeeded,
                failure_reason,
            )
            if not validation_succeeded:
                send_message_to_namespace_if_specified(
                    socketio,
                    message,
                    "start_grows_for_shelves_succeeded",
                    {"succeeded": False, "reason": failure_reason},
                )
                print("Failed validation!")
                return

            db_conn = app_config.db._new_transaction(app_config.DB_NAME)
            is_new_recipe: bool = bool(message["is_new_recipe"])
            recipe_id: Optional[int] = None
            end_date_str: Optional[str] = None
            end_date: Optional[datetime] = None
            if is_new_recipe:
                # create the recipe and the recipe phases before creating the grow
                recipe_name = (
                    message["recipe_name"] if "recipe_name" in message else None
                )
                recipe_no_id: Recipe = Recipe(None, recipe_name)
                recipe: Recipe = app_config.db.write_recipe(
                    db_conn, recipe_no_id
                )
                recipe_id = recipe.recipe_id

                light_configurations: List[Any] = message["grow_phases"]
                end_date_str = message["end_date"]
                end_date = iso8601_string_to_datetime(end_date_str)

                recipe_phases: List[
                    RecipePhase
                ] = create_recipe_phases_from_light_configurations(
                    light_configurations, recipe_id, end_date
                )
                print("recipe_phases:", recipe_phases)
                # write the recipe phases to database
                app_config.db.write_recipe_phases(db_conn, recipe_phases)

            else:
                recipe_id = message["template_recipe_id"]

            # create the grow first so we can read the grow_id
            grow_start_date: datetime = iso8601_string_to_datetime(
                message["grow_phases"][0]["start_date"]
            )
            grow_estimated_end_date: datetime = iso8601_string_to_datetime(
                message["end_date"]
            )

            current_phase: int = 0
            tag_set: str = message["tag_set"]
            nutrients: str = message["nutrients"]
            weekly_reps: int = message["weekly_reps"]
            pruning_date_1: Optional[datetime] = iso8601_string_to_datetime(
                message["pruning_date_1"]
            ) if message.get("pruning_date_1") else None
            pruning_date_2: Optional[datetime] = iso8601_string_to_datetime(
                message["pruning_date_2"]
            ) if message.get("pruning_date_2") else None

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
                tag_set,
                nutrients,
                weekly_reps,
                pruning_date_1,
                pruning_date_2,
                None,
                None,
                None,
                None,
            )

            grow: Grow = app_config.db.write_grow(db_conn, grow_without_id)

            light_configurations = message["grow_phases"]
            end_date_str = message["end_date"]
            end_date = iso8601_string_to_datetime(end_date_str)
            grow_phases: List[
                GrowPhase
            ] = create_grow_phases_from_light_configurations(
                light_configurations, grow.grow_id, recipe_id, end_date
            )

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
                db_conn,
                first_grow_phase.recipe_id,
                first_grow_phase.recipe_phase_num,
            )

            # enqueue the job to the job scheduler
            client_schedule_job(
                shelf_grows,
                first_grow_phase,
                power_level,
                red_level,
                blue_level,
            )

            # write grow phases and shelf grows to db
            app_config.db.write_grow_phases(db_conn, grow_phases)
            app_config.db.write_shelf_grows(db_conn, shelf_grows)

            print("start_grow_for_shelf succeeded!")

            # commit the transaction
            db_conn.commit()

            send_message_to_namespace_if_specified(
                socketio,
                message,
                "start_grows_for_shelves_succeeded",
                {"succeeded": True, "grow": grow.to_json()},
            )
            print("Grow started successfully, event emitted")
        except Exception as e:
            exception_str: str = str(e)
            print("Error with starting grow:", message, exception_str)
            # rollback connection and report error back to client
            db_conn.rollback()
            send_message_to_namespace_if_specified(
                socketio,
                message,
                "start_grows_for_shelves_succeeded",
                {
                    "succeeded": False,
                    "reason": "Unexpected error. Please document the conditions that lead to this error. {}".format(
                        exception_str
                    ),
                },
            )
        finally:
            if db_conn:
                # close the db connection if it's defined
                db_conn.close()

    @socketio.on("read_all_entities")
    def read_all_entities(message) -> None:
        print("read_all_entities event emitted")
        all_rooms: List[Room] = app_config.db.read_all_rooms()
        all_racks: List[Rack] = app_config.db.read_all_racks()
        all_shelves: List[Shelf] = app_config.db.read_all_shelves()
        all_current_grows: List[Grow] = app_config.db.read_current_grows()
        all_incomplete_grows: List[Grow] = app_config.db.read_incomplete_grows()

        # use set comprehensions since grows may have duplicate recipes
        current_recipe_ids = {g.recipe_id for g in all_current_grows}
        incomplete_recipe_ids = {g.recipe_id for g in all_incomplete_grows}

        current_recipe_ids.update(incomplete_recipe_ids)

        all_recipes: List[Recipe] = app_config.db.read_recipes(
            list(current_recipe_ids)
        )

        all_grow_ids = [g.grow_id for g in all_current_grows] + [
            g.grow_id for g in all_incomplete_grows
        ]
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
            "incomplete_grows": [g.to_json() for g in all_incomplete_grows],
            "grow_phases": [gp.to_json() for gp in all_grow_phases],
            "recipes": [r.to_json() for r in all_recipes],
            "recipe_phases": [rp.to_json() for rp in all_recipe_phases],
            "shelf_grows": [sg.to_json() for sg in all_current_shelf_grows],
        }

        print("Returning entities:", entities_dict)
        send_message_to_namespace_if_specified(
            socketio, message, "return_all_entities", entities_dict
        )

    @socketio.on("read_complete_grows")
    def read_complete_grows(message) -> None:
        all_complete_grows: List[Grow] = app_config.db.read_complete_grows()

        # use set comprehensions since grows may have duplicate recipes
        current_recipe_ids = {g.recipe_id for g in all_complete_grows}
        incomplete_recipe_ids = {g.recipe_id for g in all_complete_grows}

        current_recipe_ids.update(incomplete_recipe_ids)

        all_recipes: List[Recipe] = app_config.db.read_recipes(
            list(current_recipe_ids)
        )

        all_grow_ids = [g.grow_id for g in all_complete_grows]

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
            "complete_grows": [g.to_json() for g in all_complete_grows],
            "grow_phases": [gp.to_json() for gp in all_grow_phases],
            "recipes": [r.to_json() for r in all_recipes],
            "recipe_phases": [rp.to_json() for rp in all_recipe_phases],
            "shelf_grows": [sg.to_json() for sg in all_current_shelf_grows],
        }

        send_message_to_namespace_if_specified(
            socketio, message, "read_complete_grows_response", entities_dict
        )
