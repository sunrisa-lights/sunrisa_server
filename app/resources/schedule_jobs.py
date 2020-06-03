from datetime import datetime

def schedule_job_for_room(socketio, room_id, power_level, red_level, blue_level):
    print("LUCAAAAAAAAAAS! HERE", datetime.now())
    room_dict = {'room': {'room_id': room_id, 'power_level': power_level, 'red_level': red_level, 'blue_level': blue_level}}
    socketio.emit("set_lights_for_room", room_dict)
    print("Event emitted from socketio obj")
