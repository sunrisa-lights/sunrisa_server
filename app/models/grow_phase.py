from datetime import datetime, timezone, timedelta
from dateutil.parser import parse
from typing import Any, Dict
import json
import calendar


class GrowPhase:
    def __init__(
        self,
        grow_id: int,
        recipe_id: int,
        recipe_phase_num: int,
        phase_start_datetime: datetime,
        phase_end_datetime: datetime,
        is_last_phase: bool,
    ):
        self.grow_id = grow_id
        self.recipe_id = recipe_id
        self.recipe_phase_num = recipe_phase_num
        self.phase_start_datetime = phase_start_datetime
        self.phase_end_datetime = phase_end_datetime
        self.is_last_phase = is_last_phase
        self.round_dates_to_seconds()

    @classmethod
    def from_json(cls, grow_phase_json: Dict[Any, Any]):
        if not (
            "grow_id" in grow_phase_json
            and "recipe_phase_num" in grow_phase_json
            and "recipe_id" in grow_phase_json
            and "phase_start_datetime" in grow_phase_json
            and "phase_end_datetime" in grow_phase_json
            and "is_last_phase" in grow_phase_json
        ):
            raise Exception("Invalid grow phase")

        grow_id: int = int(grow_phase_json["grow_id"])
        recipe_phase_num: int = int(grow_phase_json["recipe_phase_num"])
        recipe_id: int = int(grow_phase_json["recipe_id"])
        is_last_phase: bool = bool(grow_phase_json["is_last_phase"])

        # TODO: Write methods for converting datetime -> str and vice versa
        start_date_str = grow_phase_json["phase_start_datetime"]
        end_date_str = grow_phase_json["phase_end_datetime"]

        phase_start_datetime = datetime.utcfromtimestamp(
            calendar.timegm(parse(start_date_str).utctimetuple())
        )
        phase_end_datetime = datetime.utcfromtimestamp(
            calendar.timegm(parse(end_date_str).utctimetuple())
        )
        return cls(
            grow_id,
            recipe_id,
            recipe_phase_num,
            phase_start_datetime,
            phase_end_datetime,
            is_last_phase,
        )

    def to_json(self):
        return {
            "grow_id": self.grow_id,
            "recipe_id": self.recipe_id,
            "recipe_phase_num": self.recipe_phase_num,
            "phase_start_datetime": self.phase_start_datetime.replace(microsecond=0).isoformat(),
            "phase_end_datetime": self.phase_end_datetime.replace(microsecond=0).isoformat(),
            "is_last_phase": self.is_last_phase,
        }

    # TODO: Put this in a utils file
    # Removes microseconds because they're lost in json conversions
    def round_dates_to_seconds(self):
        self.phase_start_datetime -= timedelta(microseconds=self.phase_start_datetime.microsecond)
        self.phase_end_datetime -= timedelta(microseconds=self.phase_end_datetime.microsecond)

    def __str__(self) -> str:
        return json.dumps(
            {
                "grow_id": self.grow_id,
                "recipe_phase_num": self.recipe_phase_num,
                "recipe_id": self.recipe_id,
                "phase_start_datetime": self.phase_start_datetime
                .replace(microsecond=0)
                .isoformat(),
                "phase_end_datetime": self.phase_end_datetime
                .replace(microsecond=0)
                .isoformat(),
                "is_last_phase" self.is_last_phase,
            }
        )

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if not isinstance(other, GrowPhase):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.grow_id == other.grow_id
            and self.recipe_phase_num == other.recipe_phase_num
            and self.recipe_id == other.recipe_id
            and self.phase_start_datetime == other.phase_start_datetime
            and self.phase_end_datetime == other.phase_end_datetime
            and self.is_last_phase == other.is_last_phase
        )
