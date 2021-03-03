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
from app.models.shelf_light_record import ShelfLightRecord
from app.db.grow import (
    create_grow_table,
    update_grow_harvest_data,
    move_grow_to_next_phase,
    read_current_grows,
    read_grow,
    read_complete_grows,
    read_incomplete_grows,
    update_grow_recipe,
    update_grow_dates,
    write_grow,
)
from app.db.grow_phase import (
    create_grow_phase_table,
    delete_grow_phases_from_grow,
    end_grow_phase,
    read_grow_phase,
    read_grow_phases,
    read_grow_phases_from_multiple_grows,
    update_grow_phases,
    update_grow_phases_recipe_from_grow,
    write_grow_phases,
)
from app.db.plant import create_plant_table, write_plant
from app.db.room import create_room_table, read_all_rooms, write_room
from app.db.rack import create_rack_table, write_rack, read_all_racks
from app.db.recipe import (
    create_recipe_table,
    read_recipe,
    read_recipes,
    read_recipes_with_name,
    update_recipe_name,
    write_recipe,
)
from app.db.recipe_phase import (
    create_recipe_phases_table,
    delete_recipe_phases,
    read_lights_from_recipe_phase,
    read_phases_from_recipe,
    read_phases_from_recipes,
    read_recipe_phases,
    update_recipe_phases,
    write_recipe_phases,
)
from app.db.shelf import create_shelf_table, read_all_shelves, write_shelf
from app.db.shelf_grow import (
    create_shelf_grow_table,
    read_shelves_with_grow,
    read_shelves_with_grows,
    write_shelf_grows,
)
from app.db.shelf_light_record import (
    create_shelf_light_record_table,
    get_shelf_light_records,
    write_shelf_light_records,
)


class DB:
    def __init__(self, db_name):
        self.db_name = db_name
        self.create_db(db_name)

    def _new_connection(self, db_name):
        conn = pymysql.connect(host="db", user="root", password="root")
        conn.autocommit(True)

        use_db_sql = "use {}".format(db_name)
        conn.cursor().execute(use_db_sql)

        return conn

    def _new_transaction(self) -> pymysql.connections.Connection:
        conn = pymysql.connect(host="db", user="root", password="root")
        conn.autocommit(False)

        use_db_sql = "use {}".format(self.db_name)
        conn.cursor().execute(use_db_sql)

        return conn

    def create_db(self, db_name: str) -> None:
        conn = pymysql.connect(host="db", user="root", password="root")
        conn.autocommit(True)

        create_sql: str = "create database {}".format(db_name)
        try:
            conn.cursor().execute(create_sql)
        except pymysql.err.ProgrammingError:
            print("db already exists:", db_name)
        finally:
            if conn:
                # close the connection if it's defined
                conn.close()

    def initialize_tables(self) -> None:
        db_conn = self._new_transaction()
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
            create_shelf_light_record_table(db_conn)

            # if creating all tables was successful, commit the transaction
            db_conn.commit()
        except Exception as e:
            print("Error initializing tables", str(e))
            db_conn.rollback()
            raise
        finally:
            db_conn.close()

    def delete_recipe_phases(
        self,
        db_conn: pymysql.connections.Connection,
        recipe_phases: List[RecipePhase],
    ) -> None:
        if not recipe_phases:
            return

        try:
            delete_recipe_phases(db_conn, recipe_phases)
        except Exception as e:
            print("Error deleting recipe phases:", recipe_phases, str(e))
            raise

    def delete_grow_phases_from_grow(
        self, db_conn: pymysql.connections.Connection, grow_id: int
    ) -> None:
        try:
            delete_grow_phases_from_grow(db_conn, grow_id)
        except Exception as e:
            print("Error deleting grow phases from grow:", grow_id, str(e))
            raise

    def end_grow_phase(
        self,
        db_conn: pymysql.connections.Connection,
        grow_phase: GrowPhase,
        harvest_time: datetime,
    ) -> None:
        try:
            end_grow_phase(db_conn, grow_phase, harvest_time)
        except Exception as e:
            print("Error ending grow phase:", grow_phase, harvest_time, str(e))
            raise

    def update_grow_harvest_data(
        self, db_conn: pymysql.connections.Connection, grow: Grow
    ) -> None:
        try:
            update_grow_harvest_data(db_conn, grow)
        except Exception as e:
            print("Error updating grow harvest data:", grow, str(e))
            raise

    def move_grow_to_next_phase(
        self,
        db_conn: pymysql.connections.Connection,
        grow_id: int,
        current_phase: int,
    ) -> None:
        try:
            move_grow_to_next_phase(db_conn, grow_id, current_phase)
        except Exception as e:
            print(
                "Error moving grow to next phase:",
                grow_id,
                current_phase,
                str(e),
            )
            raise

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

    def read_current_grows(self) -> List[Grow]:
        db_conn = self._new_connection(self.db_name)
        try:
            current_grows = read_current_grows(db_conn)
        finally:
            db_conn.close()
        return current_grows

    def read_complete_grows(self) -> List[Grow]:
        db_conn = self._new_connection(self.db_name)
        try:
            complete_grows = read_complete_grows(db_conn)
        finally:
            db_conn.close()
        return complete_grows

    def read_incomplete_grows(self) -> List[Grow]:
        db_conn = self._new_connection(self.db_name)
        try:
            incomplete_grows = read_incomplete_grows(db_conn)
        finally:
            db_conn.close()
        return incomplete_grows

    def read_grow_phase(
        self,
        db_conn: pymysql.connections.Connection,
        grow_id: int,
        recipe_phase_num: int,
    ) -> Optional[GrowPhase]:
        try:
            grow_phase = read_grow_phase(db_conn, grow_id, recipe_phase_num)
        except Exception as e:
            print(
                "Error reading grow phase:", grow_id, recipe_phase_num, str(e)
            )
            raise

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
            grow_phases = read_grow_phases_from_multiple_grows(
                db_conn, grow_ids
            )
        finally:
            db_conn.close()
        return grow_phases

    def read_recipe(self, recipe_id: int) -> Optional[Recipe]:
        db_conn = self._new_connection(self.db_name)
        try:
            recipe = read_recipe(db_conn, recipe_id)
        finally:
            db_conn.close()
        return recipe

    def read_recipes(self, recipe_ids: List[int]) -> List[Recipe]:
        if not recipe_ids:
            return []

        db_conn = self._new_connection(self.db_name)
        try:
            recipes = read_recipes(db_conn, recipe_ids)
        finally:
            db_conn.close()
        return recipes

    def read_recipes_with_name(self, search_name: str) -> List[Recipe]:
        db_conn = self._new_connection(self.db_name)
        try:
            recipes = read_recipes_with_name(db_conn, search_name)
        finally:
            db_conn.close()
        return recipes

    def read_phases_from_recipe(self, recipe_id: int) -> List[RecipePhase]:
        db_conn = self._new_connection(self.db_name)
        try:
            recipe_phases = read_phases_from_recipe(db_conn, recipe_id)
        finally:
            db_conn.close()
        return recipe_phases

    def read_phases_from_recipes(
        self, recipe_ids: List[int]
    ) -> List[RecipePhase]:
        if not recipe_ids:
            return []

        db_conn = self._new_connection(self.db_name)
        try:
            recipe_phases = read_phases_from_recipes(db_conn, recipe_ids)
        finally:
            db_conn.close()
        return recipe_phases

    def read_recipe_phases(
        self, recipe_id_phase_num_pairs: List[Tuple[int, int]]
    ) -> List[RecipePhase]:
        if not recipe_id_phase_num_pairs:
            return []

        db_conn = self._new_connection(self.db_name)
        try:
            recipe_phases = read_recipe_phases(
                db_conn, recipe_id_phase_num_pairs
            )
        finally:
            db_conn.close()
        return recipe_phases

    def read_lights_from_recipe_phase(
        self,
        db_conn: pymysql.connections.Connection,
        recipe_id: int,
        recipe_phase_num: int,
    ) -> Tuple[Optional[int], Optional[int], Optional[int]]:

        try:
            power_level, red_level, blue_level = read_lights_from_recipe_phase(
                db_conn, recipe_id, recipe_phase_num
            )
        except Exception as e:
            print(
                "Error reading lights from recipe phase:",
                recipe_id,
                recipe_phase_num,
                str(e),
            )
            raise

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

    def update_grow_phases(self, grow_phases: List[GrowPhase]) -> None:
        if not grow_phases:
            return

        db_conn = self._new_connection(self.db_name)
        try:
            update_grow_phases(db_conn, grow_phases)
        finally:
            db_conn.close()

    def update_grow_phases_recipe_from_grow(
        self,
        db_conn: pymysql.connections.Connection,
        grow_id: int,
        recipe_id: int,
    ) -> None:
        try:
            update_grow_phases_recipe_from_grow(db_conn, grow_id, recipe_id)
        except Exception as e:
            print(
                "Error updating grow phases recipe from grow:",
                grow_id,
                recipe_id,
                str(e),
            )
            raise

    def update_grow_recipe(
        self,
        db_conn: pymysql.connections.Connection,
        grow_id: int,
        recipe_id: int,
    ) -> None:
        try:
            update_grow_recipe(db_conn, grow_id, recipe_id)
        except Exception as e:
            print("Error updating grow recipe:", grow_id, recipe_id, str(e))
            raise

    def update_grow_dates(
        self,
        db_conn: pymysql.connections.Connection,
        grow_id: int,
        start_datetime: datetime,
        estimated_end_datetime: datetime,
    ) -> None:
        try:
            update_grow_dates(
                db_conn, grow_id, start_datetime, estimated_end_datetime
            )
        except Exception as e:
            print(
                "Error updating grow dates:",
                grow_id,
                start_datetime,
                estimated_end_datetime,
                str(e),
            )
            raise

    def update_recipe_name(
        self, db_conn: pymysql.connections.Connection, recipe: Recipe
    ) -> None:
        try:
            update_recipe_name(db_conn, recipe)
        except Exception as e:
            print("Error updating recipe name:", recipe, str(e))
            raise

    def update_recipe_phases(
        self,
        db_conn: pymysql.connections.Connection,
        recipe_phases: List[RecipePhase],
    ) -> None:
        if not recipe_phases:
            return

        try:
            update_recipe_phases(db_conn, recipe_phases)
        except Exception as e:
            print("Error writing recipe phases:", recipe_phases, str(e))
            raise

    def write_grow(
        self, db_conn: pymysql.connections.Connection, grow: Grow
    ) -> Grow:
        try:
            grow = write_grow(db_conn, grow)
        except Exception as e:
            print("Error writing grow:", grow, str(e))
            raise

        return grow

    def write_grow_phases(
        self,
        db_conn: pymysql.connections.Connection,
        grow_phases: List[GrowPhase],
    ) -> None:
        if not grow_phases:
            return

        try:
            write_grow_phases(db_conn, grow_phases)
        except Exception as e:
            print("Error writing grow phases:", grow_phases, str(e))
            raise

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

    def write_recipe(
        self, db_conn: pymysql.connections.Connection, recipe: Recipe
    ) -> Recipe:
        try:
            recipe = write_recipe(db_conn, recipe)
        except Exception as e:
            print("Error writing recipe:", recipe, str(e))
            raise

        return recipe

    def write_recipe_phases(
        self,
        db_conn: pymysql.connections.Connection,
        recipe_phases: List[RecipePhase],
    ) -> None:
        if not recipe_phases:
            return

        try:
            write_recipe_phases(db_conn, recipe_phases)
        except Exception as e:
            print("Error writing recipe phases:", recipe_phases, str(e))
            raise

    def write_shelf(self, shelf: Shelf) -> None:
        db_conn = self._new_connection(self.db_name)
        try:
            write_shelf(db_conn, shelf)
        finally:
            db_conn.close()

    def write_shelf_grows(
        self,
        db_conn: pymysql.connections.Connection,
        shelf_grows: List[ShelfGrow],
    ) -> None:
        if not shelf_grows:
            return

        try:
            write_shelf_grows(db_conn, shelf_grows)
        except Exception as e:
            print("Error writing shelf grows:", shelf_grows, str(e))
            raise

    def write_shelf_light_records(
        self,
        db_conn: pymysql.connections.Connection,
        shelf_light_records: List[ShelfLightRecord],
    ) -> None:
        if not shelf_light_records:
            return

        try:
            write_shelf_light_records(db_conn, shelf_light_records)
        except Exception as e:
            print(
                "Error writing shelf light records:",
                shelf_light_records,
                str(e),
            )
            raise

    def get_shelf_light_records(
        self, db_conn: pymysql.connections.Connection, after_date: datetime
    ) -> List[ShelfLightRecords]:
        try:
            shelf_light_records: List[ShelfLightRecord] = get_shelf_light_records(db_conn, after_date)
            return shelf_light_records
        except Exception as e:
            print("Error getting shelf light records:", after_date, str(e))
            raise
