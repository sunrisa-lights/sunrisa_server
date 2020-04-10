from typing import Any, Dict

class Room():

    def __init__(self, roomId: int, isOn: bool):
        self.roomId = roomId
        self.isOn = isOn

    @classmethod
    def from_json(cls, roomJson: Dict[Any, Any]):
        if not roomJson['roomId']:
            raise Exception("Invalid")
        roomId: int = int(roomJson['roomId'])
        isOn: bool = bool(roomJson['isOn']) if 'isOn' in roomJson else False
        return cls(roomId, isOn)

