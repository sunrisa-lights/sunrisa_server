#!/usr/bin/env python3

import eventlet

from flask import request


from flask import Flask
from flask_socketio import SocketIO
from app.views.events import init_event_listeners
from app.job_scheduler.schedule_jobs import schedule_grow_for_shelf
from app_config import AppConfig

app = Flask(__name__)
app.config["SECRET_KEY"] = "gjr38dkjn344_!67#"
app.debug = True
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/", methods=["GET", "POST"])
def index():
    print("POSSSSSSSSSSSSST")
    print("LUCAS!")
    if request.method == "POST":
        print("Request:", request, request.form)
        print("Request:", dir(request))
        params = request.form
        print("!!!! ", params["hello"])
    elif request.method == "GET":
        print("It was a get")
    else:
        print("Didn't work :(")
    return {"test": "Lucas! it works!"}


if __name__ == "__main__":
    print("Running sunrisa.py as main")
    env = "development"
    app_config = AppConfig(socketio, env)

    init_event_listeners(app_config, socketio)

    host = "0.0.0.0"
    socketio.run(app, host=host)
