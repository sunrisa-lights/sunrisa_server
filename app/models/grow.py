from datetime import datetime, timezone, timedelta
from dateutil.parser import parse
from typing import Any, Dict, Optional
import json
import calendar


class Grow:
    def __init__(
        self,
        grow_id: Optional[int],
        recipe_id: Optional[int],
        start_datetime: datetime,
        estimated_end_datetime: datetime,
        is_finished: bool,
        all_fields_complete: bool,
        olcc_number: Optional[int],
    ):
        self.grow_id = grow_id
        self.recipe_id = recipe_id
        self.start_datetime = start_datetime
        self.estimated_end_datetime = estimated_end_datetime
        self.is_finished = is_finished
        self.all_fields_complete = all_fields_complete
        self.olcc_number = olcc_number
        self.round_dates_to_seconds()

    @classmethod
    def from_json(cls, grow_json: Dict[Any, Any]):
        if not (
            "recipe_id" in grow_json
            and "start_datetime" in grow_json
            and "estimated_end_datetime" in grow_json
            and "is_finished" in grow_json
            and "all_fields_complete" in grow_json
        ):
            raise Exception("Invalid grow")

        # grow_id optional since grow might not be created yet (grow_id assigned at creation)
        grow_id: Optional[int] = grow_json.get("grow_id")
        recipe_id: int = int(grow_json["recipe_id"])
        is_finished: bool = bool(grow_json["is_finished"])
        all_fields_complete: bool = bool(grow_json["all_fields_complete"])
        olcc_number: int = int(grow_json["olcc_number"])

        # TODO: Write methods for converting datetime -> str and vice versa
        start_date_str = grow_json["start_datetime"]
        estimated_end_date_str = grow_json["estimated_end_datetime"]

        start_datetime = datetime.utcfromtimestamp(
            calendar.timegm(parse(start_date_str).utctimetuple())
        )
        estimated_end_datetime = datetime.utcfromtimestamp(
            calendar.timegm(parse(estimated_end_date_str).utctimetuple())
        )
        return cls(grow_id, recipe_id, start_datetime, estimated_end_datetime, is_finished, all_fields_complete, olcc_number)

    def to_json(self):
        return {
            "grow_id": self.grow_id,
            "recipe_id": self.recipe_id,
            "start_datetime": self.start_datetime.replace(microsecond=0).isoformat(),
            "estimated_end_datetime": self.estimated_end_datetime.replace(
                microsecond=0
            ).isoformat(),
            "is_finished": self.is_finished,
            "all_fields_complete": self.all_fields_complete,
            "olcc_number": self.olcc_number,
        }

    # Removes microseconds because they're lost in json conversionsj
    def round_dates_to_seconds(self):
        self.start_datetime -= timedelta(microseconds=self.start_datetime.microsecond)
        self.estimated_end_datetime -= timedelta(
            microseconds=self.estimated_end_datetime.microsecond
        )

    def __str__(self) -> str:
        return json.dumps(
            {
                "grow_id": self.grow_id,
                "recipe_id": self.recipe_id,
                "start_datetime": self.start_datetime.replace(
                    microsecond=0
                ).isoformat(),
                "estimated_end_datetime": self.estimated_end_datetime.replace(
                    microsecond=0
                ).isoformat(),
                "is_finished": self.is_finished,
                "all_fields_complete": self.all_fields_complete,
                "olcc_number": self.olcc_number,
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
            and self.recipe_id == other.recipe_id
            and self.start_datetime == other.start_datetime
            and self.estimated_end_datetime == other.estimated_end_datetime
            and self.is_finished == other.is_finished
            and self.all_fields_complete == other.all_fields_complete
            and self.olcc_number == other.olcc_number
        )
