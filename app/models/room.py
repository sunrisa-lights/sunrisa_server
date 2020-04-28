from typing import Any, Dict
import json


class Room:
    def __init__(self, room_id: int, is_on: bool, is_veg_room: bool):
        self.room_id = room_id
        self.is_on = is_on
        self.is_veg_room = is_veg_room

    @classmethod
    def from_json(cls, room_json: Dict[Any, Any]):
        if not "room_id" in room_json:
            raise Exception("Invalid")
        room_id: int = int(room_json["room_id"])
        is_on: bool = bool(room_json["is_on"]) if "is_on" in room_json else False
        is_veg_room: bool = bool(
            room_json["is_veg_room"]
        ) if "is_veg_room" in room_json else False
        return cls(room_id, is_on, is_veg_room)

    def to_json(self) -> Dict[str, Any]:
        return {
            "room_id": self.room_id,
            "is_on": self.is_on,
            "is_veg_room": self.is_veg_room,
        }

    def __str__(self):
        return json.dumps(
            {
                "room_id": self.room_id,
                "is_on": self.is_on,
                "is_veg_room": self.is_veg_room,
            }
        )

    def __eq__(self, other):
        if not isinstance(other, Room):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.room_id == other.room_id
            and self.is_on == other.is_on
            and self.is_veg_room == other.is_veg_room
        )
