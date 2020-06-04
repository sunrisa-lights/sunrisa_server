import pymysql

from typing import List
from typing import Optional

from app.models.room import Room
from app.models.rack import Rack
from app.models.recipe import Recipe
from app.models.shelf import Shelf
from app.models.plant import Plant
from app.db.room import create_room_table, read_all_rooms, read_room, write_room
from app.db.rack import create_rack_table, write_rack, read_racks_in_room
from app.db.recipe import create_recipe_table, write_recipe
from app.db.schedules import create_schedule_table, write_schedule_for_shelf, write_schedule_for_room
from app.db.shelf import create_shelf_table, write_shelf
from app.db.plant import create_plant_table, write_plant


class DB:
    def __init__(self, db_name, logger):
        self.logger = logger

        self.db_name = db_name
        try:
            conn = pymysql.connect(host="localhost", user="root", password="root")
            conn.autocommit(True)
            self.create_db(conn, db_name)
        finally:
            conn.close()

    def _new_connection(self, db_name):
        conn = pymysql.connect(host="localhost", user="root", password="root")
        conn.autocommit(True)

        use_db_sql = "use {}".format(db_name)
        conn.cursor().execute(use_db_sql)

        return conn

    def create_db(self, conn, db_name: str) -> None:
        conn = pymysql.connect(host="localhost", user="root", password="root")
        conn.autocommit(True)

        create_sql: str = "create database {}".format(db_name)
        try:
            conn.cursor().execute(create_sql)
        except pymysql.err.ProgrammingError:
            self.logger.debug("db already exists")
        finally:
            conn.close()

    def initialize_tables(self) -> None:
        db_conn = self._new_connection(self.db_name)
        try:
            create_room_table(db_conn)
            create_rack_table(db_conn)
            create_recipe_table(db_conn)
            create_shelf_table(db_conn)
            create_plant_table(db_conn)
            create_schedule_table(db_conn)
        finally:
            db_conn.close()

    def read_all_rooms(self) -> List[Room]:
        db_conn = self._new_connection(self.db_name)
        try:
            rooms = read_all_rooms(db_conn)
        finally:
            db_conn.close()

        return rooms

    def read_room(self, room_id: int) -> Optional[Room]:
        db_conn = self._new_connection(self.db_name)
        try:
            room = read_room(db_conn, room_id)
        finally:
            db_conn.close()
        return room

    def read_racks_in_room(self, room_id: int) -> List[Rack]:
        db_conn = self._new_connection(self.db_name)
        try:
            racks = read_racks_in_room(db_conn, room_id)
        finally:
            db_conn.close()
        return racks

    def write_room(self, room: Room) -> None:
        db_conn = self._new_connection(self.db_name)
        try:
            write_room(db_conn, room)
        finally:
            db_conn.close()

    def write_rack(self, rack: Rack) -> None:
        db_conn = self._new_connection(self.db_name)
        try:
            write_rack(db_conn, rack)
        finally:
            db_conn.close()

    def write_recipe(self, recipe: Recipe) -> None:
        db_conn = self._new_connection(self.db_name)
        try:
            write_recipe(db_conn, recipe)
        finally:
            db_conn.close()

    def write_shelf(self, shelf: Shelf) -> None:
        db_conn = self._new_connection(self.db_name)
        try:
            write_shelf(db_conn, shelf)
        finally:
            db_conn.close()

    def write_plant(self, plant: Plant) -> None:
        db_conn = self._new_connection(self.db_name)
        try:
            write_plant(db_conn, plant)
        finally:
            db_conn.close()

    def write_schedule_for_shelf(self, shelf_id: int, start_time: str, end_time: str, power_level: int, red_level: int, blue_level: int) -> None:
        db_conn = self._new_connection(self.db_name)
        try:
            write_schedule_for_shelf(db_conn, shelf_id, start_time, end_time, power_level, red_level, blue_level)
        finally:
            db_conn.close()

    def write_schedule_for_room(self, room_id: int, start_time: str, end_time: str, power_level: int, red_level: int, blue_level: int) -> None:
        db_conn = self._new_connection(self.db_name)
        try:
            write_schedule_for_shelf(db_conn, room_id, start_time, end_time, power_level, red_level, blue_level)
        finally:
            db_conn.close()
