from app.db.room import create_room_table, write_room
import pymysql.cursors

class DB():

    def __init__(self, conn, db_name, logger):
        self.logger = logger
        self.conn = conn

        self.create_and_use_db(db_name)

    def create_and_use_db(self, db_name):
        create_sql = 'create database {}'.format(db_name)
        try:
            self.conn.cursor().execute(create_sql)
        except pymysql.err.ProgrammingError:
            self.logger.debug("db already exists")

        use_sql = 'use {}'.format(db_name)
        self.conn.cursor().execute(use_sql)

    def initialize_tables(self):
        create_room_table(self.conn)

    def write_room(self, room):
        write_room(self.conn, room)
