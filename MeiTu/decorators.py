# -*- coding: utf-8 -*-
from functools import wraps

from flask_login import current_user
from flask import redirect, url_for, flash, abort
from markupsafe import Markup


def confirm_mail(view_func):
    @wraps(view_func)
    def confirm(*args, **kwargs):
        if not current_user.confirmed:
            message = Markup(
                '请通过邮箱激活您的账号。'
                '还未收到邮件?'
                '<a class="alert-link" href="{}">点击重发</a>'.format(url_for('auth.resend_confirm_email'))
            )
            flash(message, 'warning')
            return redirect(url_for('user.index', username=current_user.username))
        return view_func(*args, **kwargs)
    return confirm


def admin_required(view_func):
    @wraps(view_func)
    def confirm(*args, **kwargs):
        user = current_user._get_current_object()
        if not user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)
    return confirm
