from collections import Counter
from typing import Any, Dict, List
import json

class Rack():

    def __init__(self, rack_id: int, shelve_ids: List[int], is_on: bool, is_connected: bool):
        self.rack_id = rack_id
        self.shelve_ids = shelve_ids
        self.is_on = is_on
        self.is_connected = is_connected

    @classmethod
    def from_json(cls, rack_json: Dict[Any, Any]):
        if not 'rack_id' in rack_json or not 'shelve_ids' in rack_json:
            raise Exception("Invalid")
        rack_id: int = int(rack_json['rack_id'])
        shelve_ids: List[int] = rack_json['shelve_ids']
        is_on: bool = bool(rack_json['is_on']) if 'is_on' in rack_json else False
        is_connected: bool = bool(rack_json['is_connected']) if 'is_connected' in rack_json else False
        return cls(rack_id, shelve_ids, is_on, is_connected)

    def __str__(self):
        return json.dumps({'rack_id': self.rack_id, 'shelve_ids': self.shelve_ids, 'is_on': self.is_on, 'is_connected': self.is_connected})

    def __eq__(self, other):
        if not isinstance(other, Rack):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.rack_id == other.rack_id and Counter(self.shelve_ids) == Counter(other.shelve_ids) and self.is_on == other.is_on and self.is_connected == other.is_connected




