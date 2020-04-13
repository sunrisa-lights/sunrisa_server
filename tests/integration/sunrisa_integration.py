import socketio

# standard Python
sio = socketio.Client()
sio.connect('http://localhost:5000')

expected_processed_entities = None

def test_send_room():
    global expected_processed_entities
    expected_processed_entities = ['room']

    room_dict = {'room': {'roomId': 1, 'isOn': False}}
    sio.emit('message_sent', room_dict)


@sio.on('message_received')
def verify_message_received(entities_processed):
    assert entities_processed['processed'] == expected_processed_entities

def run_tests():
    test_send_room()
    print("Integration tests passed!")

if __name__ == "__main__":
    run_tests()

    # sleep because we get BrokenPipeError when we disconnect too fast after sending events
    sio.sleep(1)

    sio.disconnect()
