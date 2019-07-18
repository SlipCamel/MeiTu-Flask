# -*- coding: utf-8 -*-
import os
import re
from datetime import datetime

from flask import current_app
from flask_avatars import Identicon

from MeiTu.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from MeiTu.extensions import whooshee

association_table = db.Table('association_table',
                             db.Column('travel_id', db.Integer, db.ForeignKey('travels.id')),
                             db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                             )


class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    follower = db.relationship('User', foreign_keys=[follower_id], back_populates='following', lazy='joined')
    followed = db.relationship('User', foreign_keys=[followed_id], back_populates='followers', lazy='joined')


@whooshee.register_model('username', 'nick_name')
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True, index=True)
    email = db.Column(db.String(254), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    nick_name = db.Column(db.String(30))
    member_since = db.Column(db.DATETIME, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    confirmed = db.Column(db.Boolean, default=True)
    biography = db.Column(db.String(120))
    location = db.Column(db.String(50))
    public_collections = db.Column(db.Boolean, default=True)
    public_following = db.Column(db.Boolean, default=True)
    public_followers = db.Column(db.Boolean, default=True)
    receive_comment_notification = db.Column(db.Boolean, default=True)
    receive_follow_notification = db.Column(db.Boolean, default=True)
    receive_collect_notification = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    comments = db.relationship('Comment', back_populates='author', cascade='all')
    travels = db.relationship('Travels', back_populates='author', cascade='all')
    collections = db.relationship('Collect', back_populates='collector', cascade='all')
    notifications = db.relationship('Notification', back_populates='receiver', cascade='all')
    following = db.relationship('Follow', foreign_keys=[Follow.follower_id], back_populates='follower',
                                lazy='dynamic', cascade='all')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], back_populates='followed',
                                lazy='dynamic', cascade='all')
    # 头像相关
    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))
    avatar_raw = db.Column(db.String(64))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.generate_avatar()
        self.generate_bio()
        self.follow(self)

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

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user):
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    def is_following(self, user):
        if user.id is None:
            return False
        return self.following.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def unlock(self):
        self.active = True
        db.session.commit()

    def lock(self):
        self.active = False
        db.session.commit()

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

    def generate_bio(self):
        self.biography = '此用户没有个性签名啊啊啊'
        db.session.commit()


@whooshee.register_model('title')
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
    tags = db.relationship('Tag', back_populates='travels', secondary=association_table)


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


@whooshee.register_model('name')
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    travels = db.relationship('Travels', secondary=association_table, back_populates='tags')


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    receiver = db.relationship('User', back_populates='notifications')


@db.event.listens_for(User, 'after_delete', named=True)
def delete_avatars(**kwargs):
    target = kwargs['target']
    for filename in [target.avatar_s, target.avatar_m, target.avatar_l, target.avatar_raw]:
        if filename is not None:
            path = os.path.join(current_app.config['AVATARS_SAVE_PATH'], filename)
            if os.path.exists(path):
                os.remove(path)


@db.event.listens_for(User.avatar_s, 'set', named=True)
def delete_old_avatars(**kwargs):
    avatar_s = kwargs['oldvalue']
    img_name = os.path.splitext(avatar_s)[0]
    extension = os.path.splitext(avatar_s)[1]
    avatar_l = img_name[0:-2] + '_l' + extension
    avatar_m = img_name[0:-2] + '_m' + extension
    img_list = [avatar_s, avatar_l, avatar_m]
    for filename in img_list:
        path = os.path.join(current_app.config['AVATARS_SAVE_PATH'], filename)
        if os.path.exists(path):
            os.remove(path)


@db.event.listens_for(User.avatar_raw, 'set', named=True)
def delete_old_raw_avatars(**kwargs):
    avatar_raw = kwargs['oldvalue']
    path = os.path.join(current_app.config['AVATARS_SAVE_PATH'], avatar_raw)
    if os.path.exists(path):
        os.remove(path)


@db.event.listens_for(Travels, 'after_delete', named=True)
def delete_pic(**kwargs):
    target = kwargs['target']
    img_url_list = re.findall(r'src="(.*?)"', target.body)
    if len(img_url_list):
        distinct_list = list(set(img_url_list))
        img_list = [i.split('/')[-1] for i in distinct_list]
        for filename in img_list:
            path = os.path.join(current_app.config['FILE_UPLOAD'], filename)
            if os.path.exists(path):
                os.remove(path)


@db.event.listens_for(TravelHead, 'after_delete', named=True)
def delete_head(**kwargs):
    target = kwargs['target']
    for filename in [target.filename, target.filename_m]:
        if filename is not None:
            path = os.path.join(current_app.config['DROPZONE_FILE_UPLOAD'], filename)
            if os.path.exists(path):
                os.remove(path)


@db.event.listens_for(Travels.body, 'set', named=True)
def delete_oldpic(**kwargs):
    value = kwargs['value']
    old_value = kwargs['oldvalue']
    if type(old_value) is str:
        img_url_list = re.findall(r'src="(.*?)"', value)
        oldimg_url_list = re.findall(r'src="(.*?)"', old_value)
        diff_url_list = list(set(oldimg_url_list) - set(img_url_list))
        if len(diff_url_list):
            img_list = [i.split('/')[-1] for i in diff_url_list]
            for filename in img_list:
                path = os.path.join(current_app.config['FILE_UPLOAD'], filename)
                if os.path.exists(path):
                    os.remove(path)
