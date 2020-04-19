#!/bin/env python

from flask import Flask
from flask_socketio import SocketIO
from app.views.events import init_event_listeners

socketio = SocketIO()
from app_config import AppConfig


app = Flask(__name__)

def create_app(debug):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'

    env = "development"
    app_config = AppConfig(socketio, env)

    socketio.init_app(app)
    init_event_listeners(app_config, socketio)
    return app


if __name__ == '__main__':
    debug = True
    app = create_app(debug)

    socketio.run(app)
