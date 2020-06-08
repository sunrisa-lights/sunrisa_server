from datetime import datetime
from dateutil.parser import parse
from time import mktime
from typing import Any, Dict, List, Optional
import json


class Schedule:
    def __init__(
        self,
        room_id: Optional[int],
        shelf_id: Optional[int],
        start_datetime: datetime,
        end_datetime: datetime,
        power_level: int,
        red_level: int,
        blue_level: int,
    ):
        self.room_id = room_id
        self.shelf_id = shelf_id
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.power_level = power_level
        self.red_level = red_level
        self.blue_level = blue_level

    @classmethod
    def from_json(cls, schedule_json: Dict[Any, Any]):
        if not (
            ("room_id" in schedule_json or "shelf_id" in schedule_json)
            and "start_datetime" in schedule_json
            and "end_datetime" in schedule_json
            and "power_level" in schedule_json
            and "red_level" in schedule_json
            and "blue_level" in schedule_json
        ):
            raise Exception("Invalid schedule")

        room_id: Optional[int] = int(
            schedule_json["room_id"]
        ) if "room_id" in schedule_json else None
        shelf_id: Optional[int] = int(
            schedule_json["shelf_id"]
        ) if "shelf_id" in schedule_json else None

        power_level: int = int(schedule_json["power_level"])
        red_level: int = int(schedule_json["red_level"])
        blue_level: int = int(schedule_json["blue_level"])

        # TODO: Write methods for converting datetime -> str and vice versa
        start_date_str = schedule_json["start_datetime"]
        end_date_str = schedule_json["end_datetime"]

        start_datetime = datetime.fromtimestamp(
            mktime(parse(start_date_str).utctimetuple())
        )
        end_datetime = datetime.fromtimestamp(
            mktime(parse(end_date_str).utctimetuple())
        )

        return cls(
            room_id,
            shelf_id,
            start_datetime,
            end_datetime,
            power_level,
            red_level,
            blue_level,
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "room_id": self.room_id,
            "shelf_id": self.shelf_id,
            "start_datetime": self.start_datetime.astimezone()
            .replace(microsecond=0)
            .isoformat(),
            "end_datetime": self.end_datetime.astimezone()
            .replace(microsecond=0)
            .isoformat(),
            "power_level": self.power_level,
            "red_level": self.red_level,
            "blue_level": self.blue_level,
        }

    def __str__(self):
        return json.dumps(
            {
                "room_id": self.room_id,
                "shelf_id": self.shelf_id,
                "start_datetime": self.start_datetime,
                "end_datetime": self.end_datetime,
                "power_level": self.power_level,
                "red_level": self.red_level,
                "blue_level": self.blue_level,
            }
        )

    def __eq__(self, other):
        if not isinstance(other, Schedule):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.room_id == other.room_id
            and self.shelf_id == other.shelf_id
            and self.start_datetime == other.start_datetime
            and self.end_datetime == other.end_datetime
            and self.power_level == other.power_level
            and self.red_level == other.red_level
            and self.blue_level == other.blue_level
        )
