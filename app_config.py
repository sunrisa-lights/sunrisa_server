import pymysql.cursors
import logging

from app.db.db import DB

class AppConfig():

    DB_NAME = "sunrisa_test"

    def __init__(self):
        conn = pymysql.connect(host='localhost',
                               user='root',
                               password='root')

        logging.basicConfig(filename='error.log',level=logging.DEBUG)
        self.logger = logging

        self.db = DB(conn, self.DB_NAME, self.logger)

