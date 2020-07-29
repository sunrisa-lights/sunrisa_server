import pymysql

from datetime import datetime
from typing import List
from typing import Optional, Tuple

from app.models.grow import Grow
from app.models.grow_phase import GrowPhase
from app.models.plant import Plant
from app.models.room import Room
from app.models.rack import Rack
from app.models.recipe import Recipe
from app.models.recipe_phase import RecipePhase
from app.models.shelf import Shelf
from app.models.shelf_grow import ShelfGrow
from app.db.grow import (
    create_grow_table,
    harvest_grow,
    read_current_grows,
    read_grow,
    write_grow,
)
from app.db.grow_phase import (
    create_grow_phase_table,
    end_last_grow_phase,
    read_grow_phase,
    read_grow_phases,
    read_grow_phases_from_multiple_grows,
    read_last_grow_phase,
    write_grow_phases,
)
from app.db.plant import create_plant_table, write_plant
from app.db.room import create_room_table, read_all_rooms, read_room, write_room
from app.db.rack import (
    create_rack_table,
    write_rack,
    read_all_racks,
    read_racks_in_room,
)
from app.db.recipe import create_recipe_table, read_recipes, write_recipe
from app.db.recipe_phase import (
    create_recipe_phases_table,
    read_lights_from_recipe_phase,
    read_recipe_phases,
    write_recipe_phases,
)
from app.db.shelf import create_shelf_table, read_all_shelves, write_shelf
from app.db.shelf_grow import (
    create_shelf_grow_table,
    read_shelves_with_grow,
    read_shelves_with_grows,
    write_shelf_grows,
)


class DB:
    def __init__(self, db_name, logger):
        self.logger = logger

        self.db_name = db_name
        try:
            conn = pymysql.connect(
                host="db", user="root", password="root"
            )  # uses default port 3306
            conn.autocommit(True)
            self.create_db(conn, db_name)
        finally:
            conn.close()

    def _new_connection(self, db_name):
        conn = pymysql.connect(host="db", user="root", password="root")
        conn.autocommit(True)

        use_db_sql = "use {}".format(db_name)
        conn.cursor().execute(use_db_sql)

        return conn

    def create_db(self, conn, db_name: str) -> None:
        conn = pymysql.connect(host="db", user="root", password="root")
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
            create_recipe_phases_table(db_conn)
            create_grow_table(db_conn)
            create_grow_phase_table(db_conn)
            create_shelf_grow_table(db_conn)
        except Exception as e:
            print("Error initializing tables", e)
            raise
        finally:
            db_conn.close()

    def end_last_grow_phase(self, grow_phase: GrowPhase, harvest_time: datetime) -> None:
        db_conn = self._new_connection(self.db_name)
        try:
            end_last_grow_phase(db_conn, grow_phase, harvest_time)
        finally:
            db_conn.close()

    def harvest_grow(self, grow: Grow) -> None:
        db_conn = self._new_connection(self.db_name)
        try:
            harvest_grow(db_conn, grow)
        finally:
            db_conn.close()


    def read_all_racks(self) -> List[Rack]:
        db_conn = self._new_connection(self.db_name)
        try:
            racks = read_all_racks(db_conn)
        finally:
            db_conn.close()

        return racks

    def read_all_rooms(self) -> List[Room]:
        db_conn = self._new_connection(self.db_name)
        try:
            rooms = read_all_rooms(db_conn)
        finally:
            db_conn.close()

        return rooms

    def read_all_shelves(self) -> List[Shelf]:
        db_conn = self._new_connection(self.db_name)
        try:
            shelves = read_all_shelves(db_conn)
        finally:
            db_conn.close()

        return shelves

    def read_grow(self, grow_id: int) -> Optional[Grow]:
        db_conn = self._new_connection(self.db_name)
        try:
            grow = read_grow(db_conn, grow_id)
        finally:
            db_conn.close()
        return grow

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

    def read_current_grows(self) -> List[Grow]:
        db_conn = self._new_connection(self.db_name)
        try:
            current_grows = read_current_grows(db_conn)
        finally:
            db_conn.close()
        return current_grows

    def read_grow_phase(self, grow_id: int, recipe_phase_num: int) -> Optional[GrowPhase]:
        db_conn = self._new_connection(self.db_name)
        try:
            grow_phase = read_grow_phase(db_conn, grow_id, recipe_phase_num)
        finally:
            db_conn.close()
        return grow_phase

    def read_grow_phases(self, grow_id: int) -> List[GrowPhase]:
        db_conn = self._new_connection(self.db_name)
        try:
            grow_phases = read_grow_phases(db_conn, grow_id)
        finally:
            db_conn.close()
        return grow_phases

    def read_grow_phases_from_multiple_grows(
        self, grow_ids: List[int]
    ) -> List[GrowPhase]:
        if not grow_ids:
            return []

        db_conn = self._new_connection(self.db_name)
        try:
            grow_phases = read_grow_phases_from_multiple_grows(db_conn, grow_ids)
        finally:
            db_conn.close()
        return grow_phases

    def read_last_grow_phase(self, grow_id: int) -> Optional[GrowPhase]:
        db_conn = self._new_connection(self.db_name)
        try:
            grow_phase: Optional[GrowPhase] = read_last_grow_phase(db_conn, grow_id)
        finally:
            db_conn.close()
        return grow_phase

    def read_recipes(self, recipe_ids: List[int]) -> List[Recipe]:
        if not recipe_ids:
            return []

        db_conn = self._new_connection(self.db_name)
        try:
            recipes = read_recipes(db_conn, recipe_ids)
        finally:
            db_conn.close()
        return recipes

    def read_recipe_phases(
        self, recipe_id_phase_num_pairs: List[Tuple[int, int]]
    ) -> List[RecipePhase]:
        if not recipe_id_phase_num_pairs:
            return []

        db_conn = self._new_connection(self.db_name)
        try:
            recipe_phases = read_recipe_phases(db_conn, recipe_id_phase_num_pairs)
        finally:
            db_conn.close()
        return recipe_phases

    def read_lights_from_recipe_phase(
        self, recipe_id: int, recipe_phase_num: int
    ) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        db_conn = self._new_connection(self.db_name)
        try:
            power_level, red_level, blue_level = read_lights_from_recipe_phase(
                db_conn, recipe_id, recipe_phase_num
            )
        finally:
            db_conn.close()
        return power_level, red_level, blue_level

    def read_shelves_with_grow(self, grow_id: int) -> List[ShelfGrow]:
        db_conn = self._new_connection(self.db_name)
        try:
            current_shelf_grows = read_shelves_with_grow(db_conn, grow_id)
        finally:
            db_conn.close()
        return current_shelf_grows

    def read_shelves_with_grows(self, grow_ids: List[int]) -> List[ShelfGrow]:
        if not grow_ids:
            return []

        db_conn = self._new_connection(self.db_name)
        try:
            current_shelf_grows = read_shelves_with_grows(db_conn, grow_ids)
        finally:
            db_conn.close()
        return current_shelf_grows

    def write_grow(self, grow: Grow) -> Grow:
        db_conn = self._new_connection(self.db_name)
        try:
            grow = write_grow(db_conn, grow)
        finally:
            db_conn.close()

        return grow

    def write_grow_phases(self, grow_phases: List[GrowPhase]) -> None:
        if not grow_phases:
            return

        db_conn = self._new_connection(self.db_name)
        try:
            write_grow_phases(db_conn, grow_phases)
        finally:
            db_conn.close()

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

    def write_recipe(self, recipe: Recipe) -> Recipe:
        db_conn = self._new_connection(self.db_name)
        try:
            recipe = write_recipe(db_conn, recipe)
        finally:
            db_conn.close()

        return recipe

    def write_recipe_phases(self, recipe_phases: List[RecipePhase]) -> None:
        db_conn = self._new_connection(self.db_name)
        try:
            write_recipe_phases(db_conn, recipe_phases)
        finally:
            db_conn.close()

    def write_shelf(self, shelf: Shelf) -> None:
        db_conn = self._new_connection(self.db_name)
        try:
            write_shelf(db_conn, shelf)
        finally:
            db_conn.close()

    def write_shelf_grows(self, shelf_grows: List[ShelfGrow]) -> None:
        if not shelf_grows:
            return

        db_conn = self._new_connection(self.db_name)
        try:
            write_shelf_grows(db_conn, shelf_grows)
        finally:
            db_conn.close()

    def write_plant(self, plant: Plant) -> None:
        db_conn = self._new_connection(self.db_name)
        try:
            write_plant(db_conn, plant)
        finally:
            db_conn.close()
