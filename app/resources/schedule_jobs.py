from datetime import datetime

from app.models.grow import Grow


def schedule_grow_for_shelf(
    socketio, grow: Grow, power_level: int, red_level: int, blue_level: int
) -> None:
    shelf_grow_dict = {
        "grow": grow.to_json(),
        "power_level": power_level,
        "red_level": red_level,
        "blue_level": blue_level,
    }
    socketio.emit("set_lights_for_grow", shelf_grow_dict)
    print("Event emitted from socketio obj")
