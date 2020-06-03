import pymysql.cursors
import logging

from app.db.db import DB
from apscheduler.schedulers.background import BackgroundScheduler


class AppConfig:

    DB_NAME = "sunrisa_test"

    def __init__(self, sio, env):
        self.sio = sio

        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        if env == "development":
            logging.basicConfig(filename="error.log", level=logging.DEBUG)
            self.logger = logging

            self.db = DB(self.DB_NAME, self.logger)
            self.db.initialize_tables()
        else:
            raise Error("Unimplemented environment {}".format(env))
