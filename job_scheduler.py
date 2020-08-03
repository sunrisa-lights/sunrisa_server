"""The Python implementation of the GRPC helloworld.Greeter server."""

from concurrent import futures
import logging

from datetime import datetime, timedelta
import grpc
import requests

from app.job_scheduler import helloworld_pb2
from app.job_scheduler import helloworld_pb2_grpc
from app.job_scheduler.schedule_jobs import schedule_grow_for_shelf
from app.db.db import DB

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
        self.db = DB(self.DB_NAME)


def print_hello():
    print("Hello!")

def send_socketio_message():
    print("Sending a socketio message")
    # data to be sent to api 
    data = {'hello':'LUCAAAAAAAAAAAAAAAAAAS', "new_edit": "yes"} 
    
    # sending post request and saving response as response object 
    r = requests.post(url=API_ENDPOINT, data=data) 
    print("Received a response from socketio server")
    
    # extracting response text  
    pastebin_url = r.text 
    print("The pastebin URL is:%s"%pastebin_url) 


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
        self.config.job_scheduler.add_job(
            print_hello,
            "interval",
            start_date=now,
            end_date=later,
            seconds=5,  # TODO: Put this in a constants file and link with usage in schedule_jobs.py
        )
        print("Added the job to the job scheduler successfully")

        send_socketio_message()

        print("SUCCCCCESS")
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
