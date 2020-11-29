from typing import List
from datetime import datetime, timedelta

from app.models.grow_phase import GrowPhase
from app.models.shelf_grow import ShelfGrow
from app_config import AppConfig

import grpc  # type: ignore
from google.protobuf.timestamp_pb2 import Timestamp

from app.generated.python import job_scheduler_pb2  # type: ignore
from app.generated.grpc_python import job_scheduler_pb2_grpc  # type: ignore


def schedule_grow_for_shelf(
    app_config,
    shelf_grows: List[ShelfGrow],
    grow_phase: GrowPhase,
    power_level: int,
    red_level: int,
    blue_level: int,
) -> None:
    print("In schedule_grow_for_shelf")

    shelf_grow_dict = {
        "shelves": [sg.to_json() for sg in shelf_grows],
        "power_level": power_level,
        "red_level": red_level,
        "blue_level": blue_level,
    }

    app_config.sio.emit("set_lights_for_grow", shelf_grow_dict)
    print("Set_lights_for_grow event emitted")

    # check if this is the last run and we need to schedule the next phase
    schedule_next_phase_if_needed(app_config, shelf_grows, grow_phase)
    print("Successfully scheduled grow for shelf!")


def get_job_id(grow_phase: GrowPhase) -> str:
    job_id: str = "grow-{}-phase-{}".format(
        grow_phase.grow_id, grow_phase.recipe_phase_num
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

        client_schedule_job(
            shelf_grows, grow_phase, power_level, red_level, blue_level
        )

        # update `current_phase` attribute of Grow object now that we've moved to the next phase
        app_config.db.move_grow_to_next_phase(
            next_grow_phase.grow_id, next_grow_phase.recipe_phase_num
        )


def client_schedule_job(
    shelf_grows: List[ShelfGrow],
    grow_phase: GrowPhase,
    power_level: int,
    red_level: int,
    blue_level: int,
) -> None:
    with grpc.insecure_channel("sunrisa_job_scheduler:50051") as channel:
        stub = job_scheduler_pb2_grpc.JobSchedulerStub(channel)
        shelf_grow_protos = [
            job_scheduler_pb2.ShelfGrow(
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

        grow_phase_proto = job_scheduler_pb2.GrowPhase(
            grow_id=grow_phase.grow_id,
            recipe_phase_num=grow_phase.recipe_phase_num,
            recipe_id=grow_phase.recipe_id,
            phase_start_datetime=phase_start_timestamp,
            phase_end_datetime=phase_end_timestamp,
            is_last_phase=grow_phase.is_last_phase,
        )
        proto = job_scheduler_pb2.ScheduleJobRequest(
            shelf_grows=shelf_grow_protos,
            grow_phase=grow_phase_proto,
            power_level=power_level,
            red_level=red_level,
            blue_level=blue_level,
        )

        response = stub.ScheduleJob(proto)  # TODO: Add retries?
    print(
        "Job scheduler client received response from ScheduleJob: {}".format(
            response.succeeded
        )
    )


def client_remove_job(grow_phase: GrowPhase) -> None:
    with grpc.insecure_channel("sunrisa_job_scheduler:50051") as channel:
        stub = job_scheduler_pb2_grpc.JobSchedulerStub(channel)

        phase_start_timestamp = Timestamp()
        phase_start_timestamp.FromDatetime(grow_phase.phase_start_datetime)

        phase_end_timestamp = Timestamp()
        phase_end_timestamp.FromDatetime(grow_phase.phase_end_datetime)

        grow_phase_proto = job_scheduler_pb2.GrowPhase(
            grow_id=grow_phase.grow_id,
            recipe_phase_num=grow_phase.recipe_phase_num,
            recipe_id=grow_phase.recipe_id,
            phase_start_datetime=phase_start_timestamp,
            phase_end_datetime=phase_end_timestamp,
            is_last_phase=grow_phase.is_last_phase,
        )
        proto = job_scheduler_pb2.RemoveJobRequest(grow_phase=grow_phase_proto)

        response = stub.RemoveJob(proto)  # TODO: Add retries?
    print(
        "Job scheduler client received response from RemoveJob: {}".format(
            response.succeeded
        )
    )


def client_reschedule_job(
    app_config: AppConfig, old_grow_phase: GrowPhase, new_grow_phase: GrowPhase
) -> None:
    print("Removing grow phase job:", old_grow_phase)

    # first remove the old job
    client_remove_job(old_grow_phase)

    # find all shelf grows associated with this grow
    shelf_grows: List[ShelfGrow] = app_config.db.read_shelves_with_grow(
        old_grow_phase.grow_id
    )

    if not shelf_grows:
        raise Exception(
            "No shelf grows found for grow:", old_grow_phase.grow_id
        )

    (
        power_level,
        red_level,
        blue_level,
    ) = app_config.db.read_lights_from_recipe_phase(
        new_grow_phase.recipe_id, new_grow_phase.recipe_phase_num
    )

    print("Rescheduling grow phase job:", new_grow_phase)
    client_schedule_job(
        shelf_grows, new_grow_phase, power_level, red_level, blue_level
    )
