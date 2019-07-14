# -*- coding: utf-8 -*-
import os
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message

from MeiTu.extensions import mail


def async_send_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_mail(subject, to, template, **kwargs):
    app = current_app._get_current_object()
    message = Message(current_app.config['MEITU_MAIL_SUBJECT_PREFIX'] + subject, recipients=[to])
    message.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=async_send_mail, args=[app, message])
    thr.start()


def send_confirm_email(user, token, to=None):
    send_mail(subject='激活邮件', to=to or user.email, template='emails/confirm', user=user, token=token)


def send_token_email(user, token, to=None):
    send_mail(subject='动态令牌', to=to or user.email, template='emails/token', user=user, token=token)


def send_change_email_email(user, token, to=None):
    send_mail(subject='更改邮箱', to=to or user.email, template='emails/change_email', user=user, token=token)
