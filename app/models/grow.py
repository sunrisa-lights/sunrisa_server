from datetime import datetime, timezone, timedelta
from dateutil.parser import parse
from typing import Any, Dict, Optional
import json
import calendar


class Grow:
    def __init__(
        self,
        grow_id: int,
        rack_id: int,
        shelf_id: int,
        recipe_id: int,
        start_datetime: datetime,
        estimated_end_datetime: datetime,
    ):
        self.grow_id = grow_id
        self.room_id = room_id
        self.rack_id = rack_id
        self.shelf_id = shelf_id
        self.recipe_id = recipe_id
        self.start_datetime = start_datetime
        self.estimated_end_datetime = estimated_end_datetime
        self.round_dates_to_seconds()

    @classmethod
    def from_json(cls, grow_json: Dict[Any, Any]):
        if not (
            "room_id" in grow_json
            and "rack_id" in grow_json
            and "shelf_id" in grow_json
            and "recipe_id" in grow_json
            and "start_datetime" in grow_json
            and "estimated_end_datetime" in grow_json
        ):
            raise Exception("Invalid grow")

        grow_id: Optional[int] = grow_json.get("grow_id")
        room_id: int = int(grow_json["room_id"])
        rack_id: int = int(grow_json["rack_id"])
        shelf_id: int = int(grow_json["shelf_id"])
        recipe_id: int = int(grow_json["recipe_id"])

        # TODO: Write methods for converting datetime -> str and vice versa
        start_date_str = grow_json["start_datetime"]
        estimated_end_date_str = grow_json["estimated_end_datetime"]

        start_datetime = datetime.utcfromtimestamp(
            calendar.timegm(parse(start_date_str).utctimetuple())
        )
        estimated_end_datetime = datetime.utcfromtimestamp(
            calendar.timegm(parse(estimated_end_date_str).utctimetuple())
        )
        return cls(
            grow_id,
            room_id,
            rack_id,
            shelf_id,
            recipe_id,
            start_datetime,
            estimated_end_datetime,
        )

    def to_json(self):
        return {
            "grow_id": self.grow_id,
            "room_id": self.room_id,
            "rack_id": self.rack_id,
            "shelf_id": self.shelf_id,
            "recipe_id": self.recipe_id,
            "start_datetime": self.start_datetime.replace(microsecond=0).isoformat(),
            "estimated_end_datetime": self.estimated_end_datetime.replace(microsecond=0).isoformat(),
        }

    # Removes microseconds because they're lost in json conversions
    def round_dates_to_seconds(self):
        self.start_datetime -= timedelta(microseconds=self.start_datetime.microsecond)
        self.estimated_end_datetime -= timedelta(microseconds=self.estimated_end_datetime.microsecond)

    def __str__(self) -> str:
        return json.dumps(
            {
                "grow_id": self.grow_id,
                "room_id": self.room_id,
                "rack_id": self.rack_id,
                "shelf_id": self.shelf_id,
                "recipe_id": self.recipe_id,
                "start_datetime": self.start_datetime
                .replace(microsecond=0)
                .isoformat(),
                "estimated_end_datetime": self.estimated_end_datetime
                .replace(microsecond=0)
                .isoformat(),
            }
        )

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if not isinstance(other, Grow):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.grow_id == other.grow_id
            and self.room_id == other.room_id
            and self.rack_id == other.rack_id
            and self.shelf_id == other.shelf_id
            and self.recipe_id == other.recipe_id
            and self.start_datetime == other.start_datetime
            and self.estimated_end_datetime == other.estimated_end_datetime
        )
