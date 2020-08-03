from typing import List
from datetime import datetime, timedelta

from app.models.grow_phase import GrowPhase
from app.models.shelf_grow import ShelfGrow
from app_config import AppConfig


def schedule_grow_for_shelf(
    shelf_grows: List[ShelfGrow],
    grow_phase: GrowPhase,
    power_level: int,
    red_level: int,
    blue_level: int,
) -> None:
    print("In schedule_grow_for_shelf")
    """
    config = AppConfig()  # no arguments needed because it's a singleton instance

    shelf_grow_dict = {
        "shelves": [sg.to_json() for sg in shelf_grows],
        "power_level": power_level,
        "red_level": red_level,
        "blue_level": blue_level,
    }

    config.sio.emit("set_lights_for_grow", shelf_grow_dict)
    print("Event emitted from socketio obj")

    # check if this is the last run and we need to schedule the next phase
    schedule_next_phase_if_needed(config, shelf_grows, grow_phase)
    print("Succeeded!")
    """


def get_job_id(shelf_grows: List[ShelfGrow], grow_phase: GrowPhase) -> str:
    shelf_grow_job_entries: List[str] = [sg.to_job_entry() for sg in shelf_grows]
    shelf_grows_string: str = "({})".format(",".join(shelf_grow_job_entries))

    job_id: str = "grow-{}-phase-{}-shelves-{}".format(
        grow_phase.grow_id, grow_phase.recipe_phase_num, shelf_grows_string
    )
    if grow_phase.is_last_phase:
        job_id += "-last-phase"
    return job_id


def schedule_next_phase_if_needed(
    app_config: AppConfig, shelf_grows: List[ShelfGrow], grow_phase: GrowPhase
) -> None:
    if grow_phase.is_last_phase:
        # last phase runs forever
        return

    job_end_date: datetime = grow_phase.phase_end_datetime
    utc_time: datetime = datetime.utcnow()

    # TODO: Protect against possibility that job_end_date < utc_time
    time_diff: timedelta = job_end_date - utc_time
    # TODO: Put 60 into a constants file, as well as 5 (job intervals are once every 5 minutes)
    time_diff_in_minutes = time_diff.total_seconds() / 60

    if time_diff_in_minutes <= 5:
        # read the next grow phase, guaranteed to exist because this isn't the last phase
        next_recipe_phase_num: int = grow_phase.recipe_phase_num + 1
        next_grow_phase: GrowPhase = app_config.db.read_grow_phase(
            grow_phase.grow_id, next_recipe_phase_num
        )
        # read light values associated with next grow phase
        (
            power_level,
            red_level,
            blue_level,
        ) = app_config.db.read_lights_from_recipe_phase(
            next_grow_phase.recipe_id, next_grow_phase.recipe_phase_num
        )

        if next_grow_phase.is_last_phase:
            app_config.scheduler.add_job(
                schedule_grow_for_shelf,
                "interval",
                start_date=next_grow_phase.phase_start_datetime,
                args=[shelf_grows, next_grow_phase, power_level, red_level, blue_level],
                id=get_job_id(shelf_grows, grow_phase),
                minutes=1,  # TODO: Put this in a constants file and link with usage in schedule_jobs.py
            )
        else:
            app_config.scheduler.add_job(
                schedule_grow_for_shelf,
                "interval",
                start_date=next_grow_phase.phase_start_datetime,
                end_date=next_grow_phase.phase_end_datetime,
                args=[shelf_grows, grow_phase, power_level, red_level, blue_level],
                id=get_job_id(shelf_grows, grow_phase),
                minutes=1,  # TODO: Put this in a constants file and link with usage in schedule_jobs.py
            )
