from typing import Any, Dict, Optional
import json

class Recipe():

    def __init__(self, recipe_id: int, recipe_name: str, power_level: int, red_level: int, blue_level: int, num_hours: int):
        self.recipe_id = recipe_id
        self.recipe_name = recipe_name
        self.power_level = power_level
        self.red_level = red_level
        self.blue_level = blue_level
        self.num_hours = num_hours

    @classmethod
    def from_json(cls, recipe_json: Dict[Any, Any]):
        if not all(key in ['recipe_id', 'recipe_name', 'power_level', 'red_level', 'blue_level', 'num_hours'] for key in recipe_json):
            raise Exception("Invalid")

        recipe_id: int = int(recipe_json['recipe_id'])
        recipe_name: str = recipe_json['recipe_name']
        power_level: int = recipe_json['power_level']
        red_level: int = recipe_json['red_level']
        blue_level: int = recipe_json['blue_level']
        num_hours: int = recipe_json['num_hours']
        return cls(recipe_id, recipe_name, power_level, red_level, blue_level, num_hours)

    def __str__(self):
        return json.dumps({'recipe_id': self.recipe_id, 'recipe_name': self.recipe_name, 'power_level': self.power_level, 'red_level': self.red_level, 'blue_level': self.blue_level, 'num_hours': self.num_hours})

    def __eq__(self, other):
        if not isinstance(other, Recipe):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.recipe_id == other.recipe_id and self.recipe_name == other.recipe_name and self.power_level == other.power_level and self.red_level == other.red_level and self.blue_level == other.blue_level and self.num_hours == other.num_hours
