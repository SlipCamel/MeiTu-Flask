# -*- coding: utf-8 -*-
import os

from flask import Flask, render_template

from MeiTu.settings import config
from MeiTu.blueprint.auth import auth_bp
from MeiTu.blueprint.main import main_bp
from MeiTu.extensions import bootstrap

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask('MeiTu')

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.config.from_object(config[config_name])

    register_blueprint(app)
    register_extensions(app)

    return app


def register_blueprint(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_extensions(app):
    bootstrap.init_app(app)
