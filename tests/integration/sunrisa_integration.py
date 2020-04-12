import socketio

# standard Python
sio = socketio.Client()
sio.connect('http://127.0.0.1:5000')

num_connect_events = 0
num_disconnect_events = 0

@sio.event
def connect():
    num_connect_events += 1
    print("I'm connected!")

@sio.event
def connect_error():
    print("The connection failed!")

@sio.event
def disconnect():
    num_disconnect_events += 1
    print("I'm disconnected!")


def test_send_room():
    room_dict = {'room': {'roomId': 1, 'isOn': False}}
    sio.emit('message_sent', room_dict)


def run_tests():
    test_send_room()
    print("Integration tests passed!")

if __name__ == "__main__":
    run_tests()
