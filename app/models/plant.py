from typing import Any, Dict, Optional
import json


class Plant:
    def __init__(self, olcc_number: int, shelf_id: Optional[int]):
        self.olcc_number = olcc_number
        self.shelf_id = shelf_id

    @classmethod
    def from_json(cls, plant_json: Dict[Any, Any]):
        if not "olcc_number" in plant_json:
            raise Exception("Invalid")

        olcc_number: int = int(plant_json["olcc_number"])
        shelf_id: Optional[int] = plant_json.get("shelf_id")
        return cls(olcc_number, shelf_id)

    def __str__(self):
        return json.dumps(
            {"olcc_number": self.olcc_number, "shelf_id": self.shelf_id}
        )

    def __eq__(self, other):
        if not isinstance(other, Plant):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.olcc_number == other.olcc_number
            and self.shelf_id == other.shelf_id
        )
