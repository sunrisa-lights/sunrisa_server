import pymysql.cursors
import logging

from app.db.db import DB
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler


# Based off of this stack overflow answer: https://stackoverflow.com/a/6798042/13297130
# any class using this as a metaclass can only be created once, ie is a singleton
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AppConfig(metaclass=Singleton):
    DB_NAME = "sunrisa_test"

    def __init__(self, sio, env):
        self.sio = sio

        if env == "development":
            logging.basicConfig(filename="error.log", level=logging.DEBUG)
            self.logger = logging

            self.db = DB(self.DB_NAME)
            self.db.initialize_tables()
        else:
            raise Exception("Unimplemented environment {}".format(env))
