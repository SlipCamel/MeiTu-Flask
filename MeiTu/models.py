# -*- coding: utf-8 -*-
from datetime import datetime

from flask_avatars import Identicon

from MeiTu.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)
    email = db.Column(db.String(254), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    nick_name = db.Column(db.String(30))
    member_since = db.Column(db.DATETIME, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    confirmed = db.Column(db.Boolean, default=False)

    # 头像相关
    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))
    avatar_raw = db.Column(db.String(64))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.generate_avatar()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.active

    # 方法generate根据参数text生成初始头像，返回文件名列表（三个不同尺寸）
    def generate_avatar(self):
        avatar = Identicon()
        filenames = avatar.generate(text=self.username)
        self.avatar_s = filenames[0]
        self.avatar_m = filenames[1]
        self.avatar_l = filenames[2]
        db.session.commit()
