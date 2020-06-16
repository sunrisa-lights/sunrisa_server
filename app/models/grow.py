from datetime import datetime
from time import mktime
from dateutil.parser import parse
from typing import Any, Dict, Optional
import json


class Grow:
    def __init__(
        self,
        room_id: int,
        rack_id: int,
        shelf_id: int,
        recipe_id: int,
        recipe_phase_num: int,
        start_datetime: datetime,
        end_datetime: datetime,
    ):
        self.room_id = room_id
        self.rack_id = rack_id
        self.shelf_id = shelf_id
        self.recipe_id = recipe_id
        self.recipe_phase_num = recipe_phase_num
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

    @classmethod
    def from_json(cls, grow_json: Dict[Any, Any]):
        if not ("room_id" in grow_json
                and "rack_id" in grow_json
                and "shelf_id" in grow_json
                and "recipe_id" in grow_json
                and "recipe_phase_num" in grow_json
                and "start_datetime" in grow_json
                and "end_datetime" in grow_json):
            raise Exception("Invalid grow")

        room_id: int = int(grow_json["room_id"])
        rack_id: int = int(grow_json["rack_id"])
        shelf_id: int = int(grow_json["shelf_id"])
        recipe_id: int = int(grow_json["recipe_id"])
        recipe_phase_num: int = int(grow_json["recipe_phase_num"])

        # TODO: Write methods for converting datetime -> str and vice versa
        start_date_str = grow_json["start_datetime"]
        end_date_str = grow_json["end_datetime"]

        start_datetime = datetime.fromtimestamp(
            mktime(parse(start_date_str).utctimetuple())
        )
        end_datetime = datetime.fromtimestamp(
            mktime(parse(end_date_str).utctimetuple())
        )
        return cls(room_id, rack_id, shelf_id, recipe_id, recipe_phase_num, start_datetime, end_datetime)

    def to_json(self):
        return {
                "room_id": self.room_id,
                "rack_id": self.rack_id,
                "shelf_id": self.shelf_id,
                "recipe_id": self.recipe_id,
                "recipe_phase_num": self.recipe_phase_num,
                "start_datetime": self.start_datetime.astimezone()
                .replace(microsecond=0)
                .isoformat(),
                "end_datetime": self.end_datetime.astimezone()
                .replace(microsecond=0)
                .isoformat(),
            }

    def __str__(self):
        return json.dumps(
            {
                "room_id": self.room_id,
                "rack_id": self.rack_id,
                "shelf_id": self.shelf_id,
                "recipe_id": self.recipe_id,
                "recipe_phase_num": self.recipe_phase_num,
                "start_datetime": self.start_datetime.astimezone()
                .replace(microsecond=0)
                .isoformat(),
                "end_datetime": self.end_datetime.astimezone()
                .replace(microsecond=0)
                .isoformat(),
            }
        )

    def __eq__(self, other):
        if not isinstance(other, Grow):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.room_id == other.room_id
            and self.rack_id == other.rack_id
            and self.shelf_id== other.shelf_id
            and self.recipe_id == other.recipe_id
            and self.recipe_phase_num == other.recipe_phase_num
            and self.start_datetime == other.start_datetime
            and self.end_datetime == other.end_datetime
        )
