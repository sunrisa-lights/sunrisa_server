from typing import Any, List, Tuple
from datetime import datetime

from app.models.grow_phase import GrowPhase
from app.utils.time_utils import iso8601_string_to_datetime

# Finds the diff between two lists. First return argument is grow phases added, second is grow phases removed, third is grow phases modified.
# This method assumes that the lists are sorted in ascending order by recipe phase number.
def old_new_grow_phases_diff(
    old_grow_phases: List[GrowPhase], new_grow_phases: List[GrowPhase]
) -> Tuple[List[GrowPhase], List[GrowPhase], List[GrowPhase]]:
    assert verify_grow_phases_sorted_ascending(
        old_grow_phases
    ), "Old grow phases not in ascending order"
    assert verify_grow_phases_sorted_ascending(
        new_grow_phases
    ), "New grow phases not in ascending order"

    added_grow_phases: List[GrowPhase] = []
    removed_grow_phases: List[GrowPhase] = []
    modified_grow_phases: List[GrowPhase] = []

    max_list_length: int = max(len(old_grow_phases), len(new_grow_phases))

    for i in range(max_list_length):
        if i >= len(old_grow_phases):
            # no more old_grow_phases entries, this grow_phase must be added
            added_grow_phases.append(new_grow_phases[i])
        elif i >= len(new_grow_phases):
            # no more new_grow_phases entries, this grow_phase must be removed
            removed_grow_phases.append(old_grow_phases[i])
        else:
            # check if old entry is different from new entry
            old_grow_phase: GrowPhase = old_grow_phases[i]
            new_grow_phase: GrowPhase = new_grow_phases[i]

            if old_grow_phase != new_grow_phase:
                modified_grow_phases.append(new_grow_phase)

    return added_grow_phases, removed_grow_phases, modified_grow_phases


# This method verifies that the lists are sorted in ascending order by recipe phase number,
# and each recipe phase number is 1 greater than the previous.
def verify_grow_phases_sorted_ascending(grow_phases: List[GrowPhase]) -> bool:
    for i in range(len(grow_phases)):
        if i != grow_phases[i].recipe_phase_num:
            return False

    return True


# Each entry in light_configurations is a JSON dict with a power_level, red_level, blue_level, and start_date entry
def create_grow_phases_from_light_configurations(
    light_configurations: List[Any], grow_id: int, recipe_id: int, end_date: datetime
) -> List[GrowPhase]:
    grow_phases: List[GrowPhase] = []
    for i, light_config in enumerate(light_configurations):
        start_date_str: str = light_config["start_date"]
        start_date: datetime = iso8601_string_to_datetime(start_date_str)
        if i == len(light_configurations) - 1:
            # this is the last phase, use `end_date` attribute for `phase_end_datetime` and mark as last phase
            is_last_phase = True
            grow_phase: GrowPhase = GrowPhase(
                grow_id, recipe_id, i, start_date, end_date, is_last_phase
            )
        else:
            next_phase_start_date_str: str = light_configurations[i + 1]["start_date"]
            next_phase_start_date: datetime = iso8601_string_to_datetime(
                next_phase_start_date_str
            )
            is_last_phase = False
            grow_phase: GrowPhase = GrowPhase(
                grow_id, recipe_id, i, start_date, next_phase_start_date, is_last_phase
            )

        grow_phases.append(grow_phase)

    return grow_phases

def grow_phase_exists_with_phase_number(phase_number: int, grow_phases: List[GrowPhase]) -> bool:
    for grow_phase in grow_phases:
        if grow_phase.recipe_phase_num == phase_number:
            return True
    
    return False