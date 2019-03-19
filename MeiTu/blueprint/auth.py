# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required

from MeiTu.extensions import db
from MeiTu.form.auth import LoginForm, RegisterForm
from MeiTu.models import User
from MeiTu.utils import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.validate_password(form.password.data):
            if login_user(user, form.remember_me.data):
                flash('登录成功', 'info')
                return redirect_back()
            else:
                flash('你的账号已被封禁', 'warning')
                return redirect(url_for('main.index'))
        flash('邮箱或密码错误', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data.lower()
        nick_name = form.nick_name.data
        user = User(username=username, email=email, nick_name=nick_name)
        user.set_password(password)
        try:
            db.session.add(user)
            db.session.commit()
            flash('确认邮件已发出，请到邮箱确认', 'info')
        except Exception as e:
            db.session.rollback()
            raise e
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('成功登出', 'info')
    return redirect(url_for('main.index'))
