# -*- coding: utf-8 -*-
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_avatars import Avatars
from flask_mail import Mail

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manage = LoginManager()
avatars = Avatars()
mail = Mail()


@login_manage.user_loader
def load_user(user_id):
    from MeiTu.models import User
    user = User.query.get(int(user_id))
    return user
