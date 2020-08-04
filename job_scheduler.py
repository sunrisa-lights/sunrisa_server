"""The Python implementation of the GRPC helloworld.Greeter server."""

from concurrent import futures
import logging

from datetime import datetime, timedelta
from typing import List
import grpc
import requests

from app.job_scheduler import helloworld_pb2
from app.job_scheduler import helloworld_pb2_grpc
from app.job_scheduler.schedule_jobs import schedule_grow_for_shelf, get_job_id
from app.models.shelf_grow import ShelfGrow
from app.models.grow_phase import GrowPhase

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

API_ENDPOINT = 'http://sunrisa_server:5000'

class JobScheduler():
    def __init__(self):
        self.DB_NAME = 'sunrisa_test'
        jobstores = {
            "default": SQLAlchemyJobStore(
                url="mysql+pymysql://root:root@db/{}".format(
                    self.DB_NAME
                )  # TODO: Make network name (`db` in this case) configurable as env var
            )
        }

        scheduler = BackgroundScheduler(jobstores=jobstores)
        scheduler.start()
        self.job_scheduler = scheduler


def print_hello():
    print("Hello!")

def send_message_to_socketio_server(shelf_grows: List[ShelfGrow], grow_phase: GrowPhase, power_level: int, red_level: int, blue_level: int):
    print("Sending a message to  socketio server")
    # data to be sent to api 
    print("shelf_grows in job_scheduler", shelf_grows)
    data = {
        'shelf_grows': [sg.to_json() for sg in shelf_grows],
        'grow_phase': grow_phase.to_json(),
        'power_level': power_level,
        'red_level': red_level,
        'blue_level': blue_level,
            } 
    
    # sending post request and saving response as response object 
    r = requests.post(url=API_ENDPOINT, json=data) 
    print("Received a response from socketio server")
    
    # extracting response text  
    pastebin_url = r.text 
    print("The pastebin URL is:%s"%pastebin_url) 

def schedule_grow_job(scheduler, shelf_grows: List[ShelfGrow], grow_phase: GrowPhase, power_level: int, red_level: int, blue_level: int):
    if grow_phase.is_last_phase:
        # schedule this phase without an end date
        scheduler.add_job(
            send_message_to_socketio_server,
            "interval",
            start_date=grow_phase.phase_start_datetime,
            args=[shelf_grows, grow_phase, power_level, red_level, blue_level],
            id=get_job_id(shelf_grows, grow_phase),
            minutes=5,  # TODO: Put this in a constants file and link with usage in schedule_jobs.py
        )
    else:
        scheduler.add_job(
            send_message_to_socketio_server,
            "interval",
            start_date=grow_phase.phase_start_datetime,
            end_date=grow_phase.phase_end_datetime,
            args=[shelf_grows, grow_phase, power_level, red_level, blue_level],
            id=get_job_id(shelf_grows, grow_phase),
            minutes=5,  # TODO: Put this in a constants file and link with usage in schedule_jobs.py
        )



class Greeter(helloworld_pb2_grpc.GreeterServicer):

    def __init__(self):
        print("Initializing this Greeter")
        js = JobScheduler()
        self.config = js
        print("Initialized job scheduler")

    def SayHello(self, request, context):
        print("In say hello response")
        now = datetime.utcnow() + timedelta(seconds=2)
        later = now + timedelta(seconds=5)
        print("Adding a job")

        shelf_grows: List[ShelfGrow] = []    
        for shelf_grow_message in request.shelf_grows:
            shelf_grow: ShelfGrow = ShelfGrow(shelf_grow_message.grow_id, shelf_grow_message.room_id, shelf_grow_message.rack_id, shelf_grow_message.shelf_id)
            shelf_grows.append(shelf_grow)
        
        if not shelf_grows:
            raise Exception("No shelf grows!")

        gpp = request.grow_phase
        start: datetime = gpp.phase_start_datetime.ToDatetime()
        end: datetime = gpp.phase_end_datetime.ToDatetime()
        grow_phase: GrowPhase = GrowPhase(gpp.grow_id, gpp.recipe_id, gpp.recipe_phase_num, start, end, gpp.is_last_phase)
        
        schedule_grow_job(self.config.job_scheduler, shelf_grows, grow_phase, request.power_level, request.red_level, request.blue_level)
        print("Added the job to the job scheduler successfully")

        return helloworld_pb2.HelloReply(message='HOLLLA Hello, %s!' % request.name)




def serve():
    print("Serving the application")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
