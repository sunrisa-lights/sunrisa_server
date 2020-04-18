from typing import Any, Dict, Optional
import json


class Shelf:
    def __init__(self, shelf_id: int, rack_id: int, recipe_id: Optional[int]):
        self.shelf_id = shelf_id
        self.rack_id = rack_id
        self.recipe_id = recipe_id

    @classmethod
    def from_json(cls, shelf_json: Dict[Any, Any]):
        if not "shelf_id" in shelf_json or not "rack_id" in shelf_json:
            raise Exception("Invalid")

        shelf_id: int = int(shelf_json["shelf_id"])
        rack_id: int = int(shelf_json["rack_id"])
        recipe_id: Optional[int] = shelf_json.get("recipe_id")
        return cls(shelf_id, rack_id, recipe_id)

    def __str__(self):
        return json.dumps(
            {
                "shelf_id": self.shelf_id,
                "rack_id": self.rack_id,
                "recipe_id": self.recipe_id,
            }
        )

    def __eq__(self, other):
        if not isinstance(other, Shelf):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.shelf_id == other.shelf_id
            and self.rack_id == other.rack_id
            and self.recipe_id == other.recipe_id
        )
