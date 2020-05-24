from typing import Any, Dict
import json


class Rack:
    def __init__(
        self, rack_id: int, room_id: int, voltage: int, is_on: bool, is_connected: bool
    ):
        self.rack_id = rack_id
        self.room_id = room_id
        self.voltage = voltage
        self.is_on = is_on
        self.is_connected = is_connected

    @classmethod
    def from_json(cls, rack_json: Dict[Any, Any]):
        if not "rack_id" in rack_json or not "room_id" in rack_json:
            raise Exception("Invalid")

        rack_id: int = int(rack_json["rack_id"])
        room_id: int = rack_json["room_id"]
        voltage: Optional[int] = rack_json.get("voltage")
        is_on: Optional[bool] = rack_json.get("is_on")
        is_connected: Optional[bool] = rack_json.get("is_connected")
        return cls(rack_id, room_id, voltage, is_on, is_connected)

    def to_json(self) -> Dict[str, Any]:
        return {
            "rack_id": self.rack_id,
            "room_id": self.room_id,
            "voltage": self.voltage,
            "is_on": self.is_on,
            "is_connected": self.is_connected,
        }

    def __str__(self):
        return json.dumps(
            {
                "rack_id": self.rack_id,
                "room_id": self.room_id,
                "voltage": self.voltage,
                "is_on": self.is_on,
                "is_connected": self.is_connected,
            }
        )

    def __eq__(self, other):
        if not isinstance(other, Rack):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self.rack_id == other.rack_id
            and self.room_id == other.room_id
            and self.voltage == other.voltage
            and self.is_on == other.is_on
            and self.is_connected == other.is_connected
        )
