import pymysql.cursors
import logging

from app.db.db import DB


class AppConfig:

    DB_NAME = "sunrisa_test"

    def __init__(self, sio, env):
        self.sio = sio

        if env == "development":
            conn = pymysql.connect(host="localhost", user="root", password="root")
            conn.autocommit(True)

            logging.basicConfig(filename="error.log", level=logging.DEBUG)
            self.logger = logging

            self.db = DB(conn, self.DB_NAME, self.logger)
            self.db.initialize_tables()
        else:
            raise Error("Unimplemented environment {}".format(env))
