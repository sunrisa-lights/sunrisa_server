import pymysql.cursors
import logging

from app.db.db import DB

class AppConfig():
    DB_NAME = "sunrisa_test"

    def __init__(self, sio, env):
        self.sio = sio

        if env == "development":
            logging.basicConfig(level=logging.DEBUG)
            self.logger = logging

            self.db = DB(self.DB_NAME)
            self.db.initialize_tables()
        else:
            raise Exception("Unimplemented environment {}".format(env))
