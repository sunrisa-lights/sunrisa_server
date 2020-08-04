#!/usr/bin/env python3

import eventlet

from flask import request


from flask import Flask
from flask_socketio import SocketIO
from app.views.events import init_event_listeners
from app.views.routes import init_endpoint_listeners
from app.job_scheduler.schedule_jobs import schedule_grow_for_shelf
from app_config import AppConfig

app = Flask(__name__)
app.config["SECRET_KEY"] = "gjr38dkjn344_!67#"
app.debug = True
socketio = SocketIO(app, cors_allowed_origins="*")

if __name__ == "__main__":
    print("Running sunrisa.py as main")
    env = "development"
    app_config = AppConfig(socketio, env)

    init_endpoint_listeners(app_config, app)
    init_event_listeners(app_config, socketio)

    host = "0.0.0.0"
    socketio.run(app, host=host)
