import socketio


def get_jobs(sio):
    arr = []
    @sio.on("get_jobs_response")
    def get_jobs_response(message) -> None:
        print("message:", message)
        arr.append(True)

    sio.emit("get_jobs", {})

    print("Get jobs event emitted")
    curr = 0
    while not arr and curr < 5:
        sio.sleep(1)
        curr += 1

    if not arr:
        print("Timed out!")



def run_and_disconnect(test_func):
    sio = socketio.Client()
    sio.connect("http://localhost:5000")
    test_func(sio)
    sio.disconnect()


if __name__ == "__main__":
    run_and_disconnect(get_jobs)
