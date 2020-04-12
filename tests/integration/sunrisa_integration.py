import socketio

# standard Python
sio = socketio.Client()
sio.connect('http://localhost:5000')

def test_send_room():
    room_dict = {'room': {'roomId': 1, 'isOn': False}}
    sio.emit('message_sent', room_dict)


def run_tests():
    test_send_room()
    print("Integration tests passed!")

if __name__ == "__main__":
    run_tests()
    sio.sleep(1)
    sio.disconnect()
