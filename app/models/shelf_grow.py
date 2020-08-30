from typing import Any, Dict
import json


class ShelfGrow:
    def __init__(self, grow_id: int, room_id: int, rack_id: int, shelf_id: int):
        self.grow_id = grow_id
        self.room_id = room_id
        self.rack_id = rack_id
        self.shelf_id = shelf_id

    @classmethod
    def from_json(cls, shelf_grow_json: Dict[Any, Any]):
        if not (
            "grow_id" in shelf_grow_json
            and "room_id" in shelf_grow_json
            and "rack_id" in shelf_grow_json
            and "shelf_id" in shelf_grow_json
        ):
            raise Exception("Invalid shelf grow")

        grow_id: int = int(shelf_grow_json["grow_id"])
        room_id: int = int(shelf_grow_json["room_id"])
        rack_id: int = int(shelf_grow_json["rack_id"])
        shelf_id: int = int(shelf_grow_json["shelf_id"])

        return cls(grow_id, room_id, rack_id, shelf_id)

    def to_json(self):
        return {
            "grow_id": self.grow_id,
            "room_id": self.room_id,
            "rack_id": self.rack_id,
            "shelf_id": self.shelf_id,
        }

    def to_job_entry(self) -> str:
        return "(shelf-{}-rack-{}-room-{})".format(
            self.shelf_id, self.rack_id, self.room_id
        )

    def __str__(self) -> str:
        return json.dumps(
            {
                "grow_id": self.grow_id,
                "room_id": self.room_id,
                "rack_id": self.rack_id,
                "shelf_id": self.shelf_id,
            }
        )

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, ShelfGrow):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.grow_id == other.grow_id
            and self.room_id == other.room_id
            and self.rack_id == other.rack_id
            and self.shelf_id == other.shelf_id
        )
