# -*- coding: utf-8 -*-
from flask import url_for

from MeiTu.extensions import db
from MeiTu.models import Notification, Travels


def push_follow_notification(follower, receiver):
    message = '用户 <a href="%s">%s</a> 关注了你.' % \
              (url_for('user.user_index', username=follower.username), follower.username)
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_comment_notification(travel_id, receiver, page=1):
    travel = Travels.query.get_or_404(travel_id)
    travel_name = travel.title
    message = '您的游记<a href="{}#comments">{}</a> 收到新的回复.'.format(
        url_for('main.show_travels', travel_id=travel_id, page=page), travel_name)
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_collect_notification(collector, travel_id, receiver):
    travel = Travels.query.get_or_404(travel_id)
    travel_name = travel.title
    message = '用户 <a href="{}">{}</a> 收藏了你的游记 <a href="{}">{}</a>'.format(
        url_for('user.index', username=collector.username),
        collector.username,
        url_for('main.show_travels', travel_id=travel_id), travel_name)
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()
