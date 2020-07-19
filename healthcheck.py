import sys
import socketio

def healthcheck():
    healthcheck_failed = False
    try:
        sio = socketio.Client()
        sio.connect("http://localhost:5000")
        sio.disconnect()
        print("Healthcheck succeeded")
    except Exception as e:
        print("Healthcheck failed. Exception:", e)
        healthcheck_failed = True

    exit_code = 1 if healthcheck_failed else 0
    return exit_code

if __name__ == '__main__':
    exit_code = healthcheck()
    sys.exit(exit_code)

