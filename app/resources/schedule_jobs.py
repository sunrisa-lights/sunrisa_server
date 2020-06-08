from datetime import datetime


def schedule_job_for_room(
    socketio, room_id: int, power_level: int, red_level: int, blue_level: int
) -> None:
    schedule_dict = {
        "schedule": {
            "room_id": room_id,
            "power_level": power_level,
            "red_level": red_level,
            "blue_level": blue_level,
        }
    }
    socketio.emit("set_lights_for_room", schedule_dict)
    print("Event emitted from socketio obj")
