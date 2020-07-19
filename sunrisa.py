#!/usr/bin/env python3

import eventlet

eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO
from app.views.events import init_event_listeners
from app_config import AppConfig

socketio = SocketIO(cors_allowed_origins="*")

app = Flask(__name__)


def create_app(debug):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config["SECRET_KEY"] = "gjr38dkjn344_!67#"

    env = "development"
    app_config = AppConfig(socketio, env)

    socketio.init_app(app)
    init_event_listeners(app_config, socketio)
    return app


if __name__ == "__main__":
    debug = False
    app = create_app(debug)

    host = "0.0.0.0"
    socketio.run(app, host=host)
