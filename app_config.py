import pymysql.cursors

from app.db.db import DB

import logging

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


class AppConfig:
    DB_NAME = "sunrisa_test"

    def __init__(self, sio, env):
        self.sio = sio

        if env == "development":
            self.db = DB(self.DB_NAME)
            self.db.initialize_tables()
        else:
            raise Exception("Unimplemented environment {}".format(env))
