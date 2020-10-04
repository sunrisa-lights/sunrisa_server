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
        current_phase: int,
        is_new_recipe: bool,
        tag_set: str,
        nutrients: str,
        weekly_reps: int,
        pruning_date_1: Optional[datetime],
        pruning_date_2: Optional[datetime],
        harvest_weight: Optional[float],
        trim_weight: Optional[float],
        dry_weight: Optional[float],
        notes: Optional[str],
    ):
        self.grow_id = grow_id
        self.recipe_id = recipe_id
        self.start_datetime = start_datetime
        self.estimated_end_datetime = estimated_end_datetime
        self.is_finished = is_finished
        self.all_fields_complete = all_fields_complete
        self.olcc_number = olcc_number
        self.current_phase = current_phase
        self.is_new_recipe = is_new_recipe
        self.tag_set = tag_set
        self.nutrients = nutrients
        self.weekly_reps = weekly_reps
        self.pruning_date_1 = pruning_date_1
        self.pruning_date_2 = pruning_date_2
        self.harvest_weight = harvest_weight
        self.trim_weight = trim_weight
        self.dry_weight = dry_weight
        self.notes = notes
        self.round_dates_to_seconds()

    @classmethod
    def from_json(cls, grow_json: Dict[Any, Any]):
        if not (
            "recipe_id" in grow_json
            and "start_datetime" in grow_json
            and "estimated_end_datetime" in grow_json
            and "is_finished" in grow_json
            and "all_fields_complete" in grow_json
            and "current_phase" in grow_json
            and "is_new_recipe" in grow_json
            and "tag_set" in grow_json
            and "nutrients" in grow_json
            and "weekly_reps" in grow_json
        ):
            raise Exception("Invalid grow")

        # grow_id optional since grow might not be created yet (grow_id assigned at creation)
        grow_id: Optional[int] = grow_json.get("grow_id")
        recipe_id: int = int(grow_json["recipe_id"])
        is_finished: bool = bool(grow_json["is_finished"])
        all_fields_complete: bool = bool(grow_json["all_fields_complete"])
        olcc_number: int = int(grow_json["olcc_number"])
        current_phase: int = int(grow_json["current_phase"])
        is_new_recipe: bool = bool(grow_json["is_new_recipe"])
        tag_set: str = str(grow_json["tag_set"])
        nutrients: str = str(grow_json["nutrients"])
        weekly_reps: int = int(grow_json["weekly_reps"])

        # TODO: Write methods for converting datetime -> str and vice versa
        start_date_str = grow_json["start_datetime"]
        estimated_end_date_str = grow_json["estimated_end_datetime"]

        start_datetime = datetime.utcfromtimestamp(
            calendar.timegm(parse(start_date_str).utctimetuple())
        )
        estimated_end_datetime = datetime.utcfromtimestamp(
            calendar.timegm(parse(estimated_end_date_str).utctimetuple())
        )

        pruning_date_str_1 = grow_json.get("pruning_date_1")
        pruning_date_str_2 = grow_json.get("pruning_date_2")

        pruning_datetime_1 = (
            datetime.utcfromtimestamp(
                calendar.timegm(parse(pruning_date_str_1).utctimetuple())
            )
            if pruning_date_str_1
            else None
        )
        pruning_datetime_2 = (
            datetime.utcfromtimestamp(
                calendar.timegm(parse(pruning_date_str_2).utctimetuple())
            )
            if pruning_date_str_2
            else None
        )

        harvest_weight: Optional[float] = grow_json.get("harvest_weight")
        trim_weight: Optional[float] = grow_json.get("trim_weight")
        dry_weight: Optional[float] = grow_json.get("dry_weight")
        notes: Optional[str] = grow_json.get("notes")

        return cls(
            grow_id,
            recipe_id,
            start_datetime,
            estimated_end_datetime,
            is_finished,
            all_fields_complete,
            olcc_number,
            current_phase,
            is_new_recipe,
            tag_set,
            nutrients,
            weekly_reps,
            pruning_datetime_1,
            pruning_datetime_2,
            harvest_weight,
            trim_weight,
            dry_weight,
            notes,
        )

    def to_json(self):
        return {
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
            "current_phase": self.current_phase,
            "is_new_recipe": self.is_new_recipe,
            "tag_set": self.tag_set,
            "nutrients": self.nutrients,
            "weekly_reps": self.weekly_reps,
            "pruning_date_1": self.pruning_date_1.replace(
                microsecond=0
            ).isoformat(),
            "pruning_date_2": self.pruning_date_2.replace(
                microsecond=0
            ).isoformat(),
            "harvest_weight": self.harvest_weight,
            "trim_weight": self.trim_weight,
            "dry_weight": self.dry_weight,
            "notes": self.notes,
        }

    # Removes microseconds because they're lost in json conversions
    def round_dates_to_seconds(self):
        self.start_datetime -= timedelta(
            microseconds=self.start_datetime.microsecond
        )
        self.estimated_end_datetime -= timedelta(
            microseconds=self.estimated_end_datetime.microsecond
        )

        if self.pruning_date_1:
            self.pruning_date_1 -= timedelta(
                microseconds=self.pruning_date_1.microsecond
            )

        if self.pruning_date_2:
            self.pruning_date_2 -= timedelta(
                microseconds=self.pruning_date_2.microsecond
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
                "current_phase": self.current_phase,
                "is_new_recipe": self.is_new_recipe,
                "tag_set": self.tag_set,
                "nutrients": self.nutrients,
                "weekly_reps": self.weekly_reps,
                "pruning_date_1": self.pruning_date_1.replace(
                    microsecond=0
                ).isoformat()
                if self.pruning_date_1
                else None,
                "pruning_date_2": self.pruning_date_2.replace(
                    microsecond=0
                ).isoformat()
                if self.pruning_date_2
                else None,
                "harvest_weight": self.harvest_weight,
                "trim_weight": self.trim_weight,
                "dry_weight": self.dry_weight,
                "notes": self.notes,
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
            and self.current_phase == other.current_phase
            and self.is_new_recipe == other.is_new_recipe
            and self.tag_set == other.tag_set
            and self.nutrients == other.nutrients
            and self.weekly_reps == other.weekly_reps
            and self.pruning_date_1 == other.pruning_date_1
            and self.pruning_date_2 == other.pruning_date_2
            and self.harvest_weight == other.harvest_weight
            and self.trim_weight == other.trim_weight
            and self.dry_weight == other.dry_weight
            and self.notes == other.notes
        )
