from datetime import datetime, timezone, timedelta
from dateutil.parser import parse
from typing import Any, Dict, Optional
import json
import calendar


class ShelfLightRecord:
    def __init__(
        self,
        shelf_id: int,
        rack_id: int,
        room_id: int,
        red_level: int,
        blue_level: int,
        power_level: int,
        recorded_at: datetime,
    ):
        self.shelf_id = shelf_id
        self.rack_id = rack_id
        self.room_id = room_id
        self.red_level = red_level
        self.blue_level = blue_level
        self.power_level = power_level
        self.recorded_at = recorded_at
        self.round_dates_to_seconds()

    @classmethod
    def from_json(cls, shelf_light_record_json: Dict[Any, Any]):
        if not (
            "shelf_id" in shelf_light_record_json
            and "rack_id" in shelf_light_record_json
            and "room_id" in shelf_light_record_json
            and "power_level" in shelf_light_record_json
            and "red_level" in shelf_light_record_json
            and "blue_level" in shelf_light_record_json
            and "recorded_at" in shelf_light_record_json
        ):
            raise Exception("Invalid shelf light record")

        shelf_id: int = int(shelf_light_record_json["shelf_id"])
        rack_id: int = int(shelf_light_record_json["rack_id"])
        room_id: int = int(shelf_light_record_json["room_id"])
        red_level: int = int(shelf_light_record_json["red_level"])
        blue_level: int = int(shelf_light_record_json["blue_level"])
        power_level: int = int(shelf_light_record_json["power_level"])

        # TODO: Write methods for converting datetime -> str and vice versa
        recorded_at_date_str = shelf_light_record_json["recorded_at"]

        recorded_at_datetime = datetime.utcfromtimestamp(
            calendar.timegm(parse(recorded_at_date_str).utctimetuple())
        )

        return cls(
            shelf_id,
            rack_id,
            room_id,
            red_level,
            blue_level,
            power_level,
            recorded_at_datetime,
        )

    def to_json(self):
        return {
            "shelf_id": self.shelf_id,
            "rack_id": self.rack_id,
            "room_id": self.room_id,
            "red_level": self.red_level,
            "blue_level": self.blue_level,
            "power_level": self.power_level,
            "recorded_at": self.recorded_at.replace(microsecond=0).isoformat(),
        }

    # Removes microseconds because they're lost in json conversions
    def round_dates_to_seconds(self):
        self.recorded_at -= timedelta(microseconds=self.recorded_at.microsecond)

    def __str__(self) -> str:
        return json.dumps(
            {
                "shelf_id": self.shelf_id,
                "rack_id": self.rack_id,
                "room_id": self.room_id,
                "red_level": self.red_level,
                "blue_level": self.blue_level,
                "power_level": self.power_level,
                "recorded_at": self.recorded_at.replace(
                    microsecond=0
                ).isoformat(),
            }
        )

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if not isinstance(other, ShelfLightRecord):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.shelf_number == other.shelf_number
            and self.rack_number == other.rack_number
            and self.room_number == other.room_number
            and self.red_level == other.red_level
            and self.blue_level == other.blue_level
            and self.power_level == other.power_level
            and self.recorded_at == other.recorded_at
        )
