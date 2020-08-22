from typing import Any, Dict, List, Tuple
from collections import Counter

from app_config import AppConfig

from app.models.grow import Grow
from app.models.shelf import Shelf
from app.models.shelf_grow import ShelfGrow

# returns a tuple, first argument is success, second argument is reason for failure if not successful
# TODO: Create a type that represents the return argument here
def validate_start_grows_for_shelves(
    app_config: AppConfig, message
) -> Tuple[bool, str]:
    if "grow_phases" not in message:
        return (False, "Grow phases not included")
    elif "shelves" not in message:
        return (False, "Shelves not included")
    elif "is_new_recipe" not in message:
        return (False, "Not specified whether this is a new recipe")
    elif "end_date" not in message:
        return (False, "End date not specified")

    shelves: List[Shelf] = parse_shelves_from_message(message)
    if not shelves:
        return (False, "No shelves specified")

    invalid_shelves: List[Shelf] = validate_all_shelves_free(app_config, shelves)
    if invalid_shelves:
        print("Invalid shelves:", invalid_shelves)
        return (False, "Not all specified shelves are free")

    return (True, "")


def validate_grow_id(
    app_config: AppConfig, message
) -> Tuple[bool, str]:
    if "grow" not in message:
        return (False, "Grow not included")

    grow_json = message["grow"]

    if "grow_id" not in grow_json:
        return (False, "Grow ID not included")

    growid: int = int(grow_json["grow_id"])

    return (True, str(growid))



# returns the list of shelves specified from caller. Throws exception if shelves are invalid.
def parse_shelves_from_message(message) -> List[Shelf]:
    shelf_json_list: List[Any] = message["shelves"]

    shelves: List[Shelf] = [
        Shelf.from_json(shelf_json) for shelf_json in shelf_json_list
    ]
    return shelves


# Returns a list of all shelves that are currently in use that are in the planned_shelf_grows list
def validate_all_shelves_free(
    app_config: AppConfig, planned_shelves: List[Shelf]
) -> List[ShelfGrow]:
    # find all current grows and the shelves used to grow them
    all_current_grows: List[Grow] = app_config.db.read_current_grows()
    all_grow_ids: List[int] = [g.grow_id for g in all_current_grows]
    all_current_used_shelf_grows: List[
        ShelfGrow
    ] = app_config.db.read_shelves_with_grows(all_grow_ids)

    # verify that none of the shelf grows are the same as the shelf grows currently in use

    # convert the shelf grows to shelves so we can ignore the grow_id attribute
    current_shelves_dict: Dict[ShelfGrow, bool] = {
        Shelf(sg.shelf_id, sg.room_id, sg.rack_id): True
        for sg in all_current_used_shelf_grows
    }

    in_use_shelves: List[Shelf] = []
    for shelf in planned_shelves:
        if shelf in current_shelves_dict:
            in_use_shelves.append(shelf)

    return in_use_shelves
def test_validate_grow_id():
    print("error message", validate_grow_id({"Notgrow": 50}))
