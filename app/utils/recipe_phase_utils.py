from typing import Any, List, Tuple

from datetime import datetime, timedelta

from app.models.recipe_phase import RecipePhase
from app.utils.time_utils import iso8601_string_to_datetime

# Finds the diff between two lists. First return argument is recipe phases added, second is recipe phases removed, third is recipe phases modified.
# This method assumes that the lists are sorted in ascending order by recipe phase number.
def old_new_recipe_phases_diff(
    old_recipe_phases: List[RecipePhase], new_recipe_phases: List[RecipePhase]
) -> Tuple[List[RecipePhase], List[RecipePhase], List[RecipePhase]]:
    assert verify_recipe_phases_sorted_ascending(
        old_recipe_phases
    ), "Old recipe phases not in ascending order"
    assert verify_recipe_phases_sorted_ascending(
        new_recipe_phases
    ), "New recipe phases not in ascending order"

    added_recipe_phases: List[RecipePhase] = []
    removed_recipe_phases: List[RecipePhase] = []
    modified_recipe_phases: List[RecipePhase] = []

    max_list_length: int = max(len(old_recipe_phases), len(new_recipe_phases))

    for i in range(max_list_length):
        if i >= len(old_recipe_phases):
            # no more old_recipe_phases entries, this recipe_phase must be added
            added_recipe_phases.append(new_recipe_phases[i])
        elif i >= len(new_recipe_phases):
            # no more new_recipe_phases entries, this recipe_phase must be removed
            removed_recipe_phases.append(old_recipe_phases[i])
        else:
            # check if old entry is different from new entry
            old_recipe_phase: RecipePhase = old_recipe_phases[i]
            new_recipe_phase: RecipePhase = new_recipe_phases[i]

            if old_recipe_phase != new_recipe_phase:
                modified_recipe_phases.append(new_recipe_phase)

    return added_recipe_phases, removed_recipe_phases, modified_recipe_phases


# This method verifies that the lists are sorted in ascending order by recipe phase number,
# and each recipe phase number is 1 greater than the previous.
def verify_recipe_phases_sorted_ascending(
    recipe_phases: List[RecipePhase]
) -> bool:
    for i in range(len(recipe_phases)):
        if i != recipe_phases[i].recipe_phase_num:
            return False

    return True


# Each entry in light_configurations is a JSON dict with a power_level, red_level, blue_level, and start_date entry
def create_recipe_phases_from_light_configurations(
    light_configurations: List[Any], recipe_id: int, end_date: datetime
) -> List[RecipePhase]:

    recipe_phases: List[RecipePhase] = []
    for i, light_config in enumerate(light_configurations):
        start_date_str: str = light_config["start_date"]
        phase_start_date: datetime = iso8601_string_to_datetime(start_date_str)

        is_last_phase = i == len(light_configurations) - 1
        # if this is the last phase, use `end_date`. Else, use the next phases start date (guaranteed to exist cause
        # this is therefore not the last phase)
        phase_end_date: datetime = end_date if is_last_phase else iso8601_string_to_datetime(
            light_configurations[i + 1]["start_date"]
        )

        date_diff: timedelta = phase_end_date - phase_start_date
        # 60 seconds * 60 minutes = 3600 seconds in an hour
        num_hours: int = int(date_diff.total_seconds() / 3600)
        recipe_phase_num: int = i
        power_level: int = light_config["power_level"]
        red_level: int = light_config["red_level"]
        blue_level: int = light_config["blue_level"]

        recipe_phase: RecipePhase = RecipePhase(
            recipe_id,
            recipe_phase_num,
            num_hours,
            power_level,
            red_level,
            blue_level,
        )
        recipe_phases.append(recipe_phase)

    print("recipe_phases:", recipe_phases)
    return recipe_phases


def recipe_phase_exists_with_phase_number(
    phase_number: int, recipe_phases: List[RecipePhase]
) -> bool:
    for recipe_phase in recipe_phases:
        if recipe_phase.recipe_phase_num == phase_number:
            return True

    return False
