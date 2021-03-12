from concurrent import futures

from datetime import datetime, timedelta
from typing import List
import grpc
import requests

from app.generated import job_scheduler_pb2, job_scheduler_pb2_grpc
from app.job_scheduler.schedule_jobs import schedule_grow_for_shelf, get_job_id
from app.models.shelf_grow import ShelfGrow
from app.models.grow_phase import GrowPhase

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.job import Job

API_ENDPOINT = "http://sunrisa_server:5000/add-job"
SYNC_GROWS_ENDPOINT = "http://sunrisa_server:5000/sync-grows"

SYNC_GROWS_JOB = "sync_grows_job"


def send_message_to_socketio_server(
    shelf_grows: List[ShelfGrow],
    grow_phase: GrowPhase,
    power_level: int,
    red_level: int,
    blue_level: int,
):
    print("Sending a message to  socketio server")
    # data to be sent to api
    print("shelf_grows in job_scheduler", shelf_grows)
    data = {
        "shelf_grows": [sg.to_json() for sg in shelf_grows],
        "grow_phase": grow_phase.to_json(),
        "power_level": power_level,
        "red_level": red_level,
        "blue_level": blue_level,
    }

    # sending post request and saving response as response object
    r = requests.post(url=API_ENDPOINT, json=data)
    print("Received a response from socketio server")

    # raises exception if non-2xx code is returned
    r.raise_for_status()


def sync_grows():
    print("Sync grows called!")
    r = requests.post(url=SYNC_GROWS_ENDPOINT)

    # raises exception if non-2xx code is returned
    r.raise_for_status()


# schedules a job for syncing the pi grows with the
# grows stored in the database
def schedule_grow_sync_job(scheduler):
    # first get jobs currently running and check if sync job already exists
    current_jobs: List[Job] = get_scheduler_jobs(scheduler)
    print("found jobs:", current_jobs)
    for job in current_jobs:
        if job.id == SYNC_GROWS_JOB:
            # grow job is already running
            print("Returning early because sync grow job already exists")
            return

    print("sync grow job not found, adding it to scheduler")
    # grow job is not running. Schedule it
    job = scheduler.add_job(
        sync_grows,
        "interval",
        id=SYNC_GROWS_JOB,
        minutes=1,  # TODO: Put this in a constants file
    )
    print("scheduled grow job:", job)


def schedule_grow_job(
    scheduler,
    shelf_grows: List[ShelfGrow],
    grow_phase: GrowPhase,
    power_level: int,
    red_level: int,
    blue_level: int,
):
    if grow_phase.is_last_phase:
        # schedule this phase without an end date
        job = scheduler.add_job(
            send_message_to_socketio_server,
            "interval",
            start_date=grow_phase.phase_start_datetime,
            args=[shelf_grows, grow_phase, power_level, red_level, blue_level],
            id=get_job_id(grow_phase),
            minutes=5,  # TODO: Put this in a constants file and link with usage in schedule_jobs.py
        )
    else:
        job = scheduler.add_job(
            send_message_to_socketio_server,
            "interval",
            start_date=grow_phase.phase_start_datetime,
            end_date=grow_phase.phase_end_datetime,
            args=[shelf_grows, grow_phase, power_level, red_level, blue_level],
            id=get_job_id(grow_phase),
            minutes=5,  # TODO: Put this in a constants file and link with usage in schedule_jobs.py
        )

    print("Scheduled job with id:", job.id)


def remove_grow_job(scheduler, grow_phase: GrowPhase) -> None:
    grow_id: str = get_job_id(grow_phase)
    scheduler.remove_job(grow_id)  # this will throw exception if job not found


def get_scheduler_jobs(scheduler) -> List[Job]:
    jobs: List[Job] = scheduler.get_jobs()
    return jobs


class JobScheduler(job_scheduler_pb2_grpc.JobSchedulerServicer):
    def __init__(self):
        db_name = "sunrisa_test"
        jobstores = {
            "default": SQLAlchemyJobStore(
                url="mysql+pymysql://root:root@db/{}".format(
                    db_name
                )  # TODO: Make network name (`db` in this case) configurable as env var
            )
        }

        scheduler = BackgroundScheduler(jobstores=jobstores)
        scheduler.start()
        self.job_scheduler = scheduler

    def ScheduleJob(self, request, context):
        if not request.shelf_grows:
            return job_scheduler_pb2.ScheduleJobReply(
                succeeded=False, reason="No shelf grows sent"
            )
        elif not request.grow_phase:
            return job_scheduler_pb2.ScheduleJobReply(
                succeeded=False, reason="No grow phase sent"
            )

        shelf_grows: List[ShelfGrow] = []
        for shelf_grow_message in request.shelf_grows:
            shelf_grow: ShelfGrow = ShelfGrow(
                shelf_grow_message.grow_id,
                shelf_grow_message.room_id,
                shelf_grow_message.rack_id,
                shelf_grow_message.shelf_id,
            )
            shelf_grows.append(shelf_grow)

        gpp = request.grow_phase
        start: datetime = gpp.phase_start_datetime.ToDatetime()
        end: datetime = gpp.phase_end_datetime.ToDatetime()
        grow_phase: GrowPhase = GrowPhase(
            gpp.grow_id,
            gpp.recipe_id,
            gpp.recipe_phase_num,
            start,
            end,
            gpp.is_last_phase,
        )

        schedule_grow_job(
            self.job_scheduler,
            shelf_grows,
            grow_phase,
            request.power_level,
            request.red_level,
            request.blue_level,
        )
        print("Added the job to the job scheduler successfully")

        return job_scheduler_pb2.ScheduleJobReply(succeeded=True)

    def RemoveJob(self, request, context):
        gpp = request.grow_phase
        start: datetime = gpp.phase_start_datetime.ToDatetime()
        end: datetime = gpp.phase_end_datetime.ToDatetime()
        grow_phase: GrowPhase = GrowPhase(
            gpp.grow_id,
            gpp.recipe_id,
            gpp.recipe_phase_num,
            start,
            end,
            gpp.is_last_phase,
        )
        remove_grow_job(self.job_scheduler, grow_phase)
        return job_scheduler_pb2.RemoveJobReply(succeeded=True)

    def GetJobs(self, request, context):
        jobs: List[Job] = get_scheduler_jobs(self.job_scheduler)
        job_protos = []
        for job in jobs:
            job_proto = job_scheduler_pb2.Job(id=job.id)
            job_protos.append(job_proto)

        return job_scheduler_pb2.GetJobsReply(jobs=job_protos)


def serve():
    print("Starting the job scheduler")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    job_scheduler: JobScheduler = JobScheduler()
    job_scheduler_pb2_grpc.add_JobSchedulerServicer_to_server(
        job_scheduler, server
    )

    # schedule grow sync job on startup if needed
    schedule_grow_sync_job(job_scheduler.job_scheduler)

    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
