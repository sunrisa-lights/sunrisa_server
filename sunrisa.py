#!/usr/bin/env python3

import eventlet

eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO
from app.views.events import init_event_listeners
from app_config import AppConfig


def create_app(debug):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config["SECRET_KEY"] = "gjr38dkjn344_!67#"

    socketio = SocketIO(app)
    socketio.init_app(app, cors_allowed_origins="*")

    env = "development"
    app_config = AppConfig(socketio, env)

    init_event_listeners(app_config, socketio)
    return socketio, app


if __name__ == "__main__":
    debug = True
    socketio, app = create_app(debug)

    host = "0.0.0.0"
    socketio.run(app, host=host)
