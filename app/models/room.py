from typing import Any, Dict
import json

class Room():

    def __init__(self, roomId: int, isOn: bool, isVegRoom: bool):
        self.roomId = roomId
        self.isOn = isOn
        self.isVegRoom = isVegRoom

    @classmethod
    def from_json(cls, roomJson: Dict[Any, Any]):
        if not 'roomId' in roomJson:
            raise Exception("Invalid")
        roomId: int = int(roomJson['roomId'])
        isOn: bool = bool(roomJson['isOn']) if 'isOn' in roomJson else False
        isVegRoom: bool = bool(roomJson['isVegRoom']) if 'isVegRoom' in roomJson else False
        return cls(roomId, isOn, isVegRoom)

    def __str__(self):
        return json.dumps({'roomId': self.roomId, 'isOn': self.isOn, 'isVegRoom': self.isVegRoom})

    def __eq__(self, other):
        if not isinstance(other, Room):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.roomId == other.roomId and self.isOn == other.isOn and self.isVegRoom == other.isVegRoom




