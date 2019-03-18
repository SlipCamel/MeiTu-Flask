# -*- coding: utf-8 -*-
import os

from flask import Flask
from MeiTu.settings import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask('MeiTu')
    app.config.from_object(config[config_name])

    @app.route('/')
    def hello():
        return 'hello'

    return app
