from typing import Any, Dict, Optional
import json


class Shelf:
    def __init__(self, shelf_id: int, room_id: int, rack_id: int):
        self.shelf_id = shelf_id
        self.room_id = room_id
        self.rack_id = rack_id

    @classmethod
    def from_json(cls, shelf_json: Dict[Any, Any]):
        if (
            not "shelf_id" in shelf_json
            or not "rack_id" in shelf_json
            or not "room_id" in shelf_json
        ):
            raise Exception("Invalid shelf")

        shelf_id: int = int(shelf_json["shelf_id"])
        room_id: int = int(shelf_json["room_id"])
        rack_id: int = int(shelf_json["rack_id"])
        return cls(shelf_id, room_id, rack_id)

    def to_json(self) -> Dict[str, Any]:
        return {
            "shelf_id": self.shelf_id,
            "room_id": self.room_id,
            "rack_id": self.rack_id,
        }

    def __str__(self):
        return json.dumps(
            {
                "shelf_id": self.shelf_id,
                "room_id": self.room_id,
                "rack_id": self.rack_id,
            }
        )

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, Shelf):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.shelf_id == other.shelf_id
            and self.rack_id == other.rack_id
            and self.room_id == other.room_id
        )
