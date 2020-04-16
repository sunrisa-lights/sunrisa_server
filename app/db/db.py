import pymysql.cursors

from app.models.room import Room
from app.models.rack import Rack
from app.models.recipe import Recipe
from app.models.shelf import Shelf
from app.db.room import create_room_table, write_room
from app.db.rack import create_rack_table, write_rack
from app.db.recipe import create_recipe_table, write_recipe
from app.db.shelf import create_shelf_table, write_shelf

class DB():

    def __init__(self, conn, db_name, logger):
        self.logger = logger
        self.conn = conn

        self.create_and_use_db(db_name)

    def create_and_use_db(self, db_name: str) -> None:
        create_sql: str  = 'create database {}'.format(db_name)
        try:
            self.conn.cursor().execute(create_sql)
        except pymysql.err.ProgrammingError:
            self.logger.debug("db already exists")

        use_sql = 'use {}'.format(db_name)
        self.conn.cursor().execute(use_sql)

    def initialize_tables(self) -> None:
        create_room_table(self.conn)
        create_rack_table(self.conn)
        create_recipe_table(self.conn)
        create_shelf_table(self.conn)

    def write_room(self, room: Room) -> None:
        write_room(self.conn, room)

    def write_rack(self, rack: Rack) -> None:
        write_rack(self.conn, rack)

    def write_recipe(self, recipe: Recipe) -> None:
        write_recipe(self.conn, recipe)

    def write_shelf(self, shelf: Shelf) -> None:
        write_shelf(self.conn, shelf)
