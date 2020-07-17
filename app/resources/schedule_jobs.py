from datetime import datetime

from app.models.grow import Grow
from app_config import AppConfig


def schedule_grow_for_shelf(
    grow: Grow, grow_end_datetime: datetime, power_level: int, red_level: int, blue_level: int
) -> None:
    config = AppConfig()  # no arguments needed because it's a singleton instance
    shelf_grow_dict = {
        "grow": grow.to_json(),
        "power_level": power_level,
        "red_level": red_level,
        "blue_level": blue_level,
    }
    config.sio.emit("set_lights_for_grow", shelf_grow_dict)
    print("Event emitted from socketio obj")
