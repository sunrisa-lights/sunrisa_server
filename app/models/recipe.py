from dateutil.parser import parse
from typing import Any, Dict, Optional
import json


class Recipe:
    def __init__(
        self,
        recipe_id: int,
        recipe_name: Optional[str],
    ):
        self.recipe_id = recipe_id
        self.recipe_name = recipe_name

    @classmethod
    def from_json(cls, recipe_json: Dict[Any, Any]):
        if not "recipe_id" in recipe_json:
            raise Exception("Invalid recipe")

        recipe_id: int = int(recipe_json["recipe_id"])
        recipe_name: Optional[str] = recipe_json.get("recipe_name")

        return cls(recipe_id, recipe_name)

    def __str__(self):
        return json.dumps(
            {
                "recipe_id": self.recipe_id,
                "recipe_name": self.recipe_name,
            }
        )

    def __eq__(self, other):
        if not isinstance(other, Recipe):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.recipe_id == other.recipe_id
            and self.recipe_name == other.recipe_name
        )
