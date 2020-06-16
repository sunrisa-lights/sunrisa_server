from dateutil.parser import parse
from typing import Any, Dict, List, Optional
import json


class RecipePhase:
    def __init__(
        self,
        recipe_id: int,
        recipe_phase_num: int,
        num_hours: int,
        power_level: int,
        red_level: int,
        blue_level: int,
    ):
        self.recipe_id = recipe_id
        self.recipe_phase_num = recipe_phase_num
        self.num_hours = num_hours
        self.power_level = power_level
        self.red_level = red_level
        self.blue_level = blue_level

    @classmethod
    def from_json(cls, recipe_phase_json: Dict[Any, Any]):
        if not (
            "recipe_id" in recipe_phase_json
            and "recipe_phase_num" in recipe_phase_json
            and "num_hours" in recipe_phase_json
            and "power_level" in recipe_phase_json
            and "red_level" in recipe_phase_json
            and "blue_level" in recipe_phase_json
        ):
            raise Exception("Invalid recipe_phase")

        recipe_id: int = int(recipe_phase_json["recipe_id"])
        recipe_phase_num: int = int(recipe_phase_json["recipe_phase_num"])
        num_hours: int = int(recipe_phase_json["num_hours"])
        power_level: int = int(recipe_phase_json["power_level"])
        red_level: int = int(recipe_phase_json["red_level"])
        blue_level: int = int(recipe_phase_json["blue_level"])

        return cls(
            recipe_id,
            recipe_phase_num,
            num_hours,
            power_level,
            red_level,
            blue_level,
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "recipe_id": self.recipe_id,
            "recipe_phase_num": self.recipe_phase_num,
            "num_hours": self.num_hours,
            "power_level": self.power_level,
            "red_level": self.red_level,
            "blue_level": self.blue_level,
        }

    def __str__(self):
        return json.dumps(
            {
                "recipe_id": self.recipe_id,
                "recipe_phase_num": self.recipe_phase_num,
                "num_hours": self.num_hours,
                "power_level": self.power_level,
                "red_level": self.red_level,
                "blue_level": self.blue_level,
            }
        )

    def __eq__(self, other):
        if not isinstance(other, recipe_phase):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.recipe_id == other.recipe_id
            and self.recipe_phase_num == other.recipe_phase_num
            and self.num_hours == other.num_hours
            and self.power_level == other.power_level
            and self.red_level == other.red_level
            and self.blue_level == other.blue_level
        )
