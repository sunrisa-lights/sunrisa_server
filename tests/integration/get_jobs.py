import socketio


def get_jobs(sio):
    @sio.on("get_jobs_response")
    def get_jobs_response(message) -> None:
        message_dict = json.loads(message)
        print("message:", message)

    sio.emit("get_jobs", {})

    print("Get jobs event emitted")


def run_and_disconnect(test_func):
    sio = socketio.Client()
    sio.connect("http://localhost:5000")
    test_func(sio)
    sio.disconnect()


if __name__ == "__main__":
    run_and_disconnect(get_jobs)
