# -*- coding: utf-8 -*-
import os

import click
from flask import Flask, render_template

from MeiTu.settings import config
from MeiTu.extensions import bootstrap, db, login_manage, avatars, mail
from MeiTu.models import User


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask('MeiTu')

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.config.from_object(config[config_name])

    register_blueprint(app)
    register_extensions(app)
    register_commands(app)

    return app


def register_blueprint(app):
    from MeiTu.blueprint.auth import auth_bp
    from MeiTu.blueprint.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manage.init_app(app)
    avatars.init_app(app)
    mail.init_app(app)


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='create or create after drop')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop database...')
        db.create_all()
        click.echo('initialize db success...')

    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='The password used to login.')
    def init(username, password):
        user = User.query.first()
        if user is not None:
            click.echo('The administrator already exists, updating...')
            user.username = username
            user.set_password(password)
        else:
            user = User(username='admin')
            user.set_password(password)
            db.session.add(user)
        db.session.commit()
        click.echo('Done')
