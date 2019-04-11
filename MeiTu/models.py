# -*- coding: utf-8 -*-
import os
from datetime import datetime

from flask import current_app
from flask_avatars import Identicon

from MeiTu.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True, index=True)
    email = db.Column(db.String(254), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    nick_name = db.Column(db.String(30))
    member_since = db.Column(db.DATETIME, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    confirmed = db.Column(db.Boolean, default=False)
    biography = db.Column(db.String(120))
    location = db.Column(db.String(50))
    public_collections = db.Column(db.Boolean, default=True)

    comments = db.relationship('Comment', back_populates='author', cascade='all')
    travels = db.relationship('Travels', back_populates='author', cascade='all')
    collections = db.relationship('Collect', back_populates='collector', cascade='all')
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

    def collect(self, travel):
        if not self.is_collecting(travel):
            collect = Collect(collector=self, collected=travel)
            db.session.add(collect)
            db.session.commit()

    def uncollect(self, travel):
        collect = Collect.query.with_parent(self).filter_by(collected_id=travel.id).first()
        if collect:
            db.session.delete(collect)
            db.session.commit()

    def is_collecting(self, travel):
        return Collect.query.with_parent(self).filter_by(collected_id=travel.id).first()

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


class Travels(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(30), unique=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    can_comment = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    author = db.relationship('User', back_populates='travels')
    travel_head = db.relationship('TravelHead', uselist=False, cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='travel', cascade='all, delete-orphan')
    collectors = db.relationship('Collect', back_populates='collected', cascade='all')


class TravelHead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(60))
    filename_m = db.Column(db.String(60))

    travels_id = db.Column(db.Integer, db.ForeignKey('travels.id'))

    travels = db.relationship('Travels')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    travel_id = db.Column(db.Integer, db.ForeignKey('travels.id'))
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))

    author = db.relationship('User', back_populates='comments')
    travel = db.relationship('Travels', back_populates='comments')
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])


class Collect(db.Model):
    collector_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    collected_id = db.Column(db.Integer, db.ForeignKey('travels.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    collector = db.relationship('User', back_populates='collections', lazy='joined')
    collected = db.relationship('Travels', back_populates='collectors', lazy='joined')
