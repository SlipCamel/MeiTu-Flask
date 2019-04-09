# -*- coding: utf-8 -*-
import random

from flask import Blueprint, render_template, redirect, url_for, flash, abort, jsonify
from flask_login import current_user, login_user, logout_user, login_required

from MeiTu.extensions import db, cache
from MeiTu.form.auth import LoginForm, RegisterForm, ForgetPasswordForm, ForgetPasswordResetForm
from MeiTu.models import User
from MeiTu.utils import redirect_back, generate_token, validate_token
from MeiTu.email_tool import send_confirm_email, send_token_email
from MeiTu.settings import Operations

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
                return redirect(url_for('main.login'))
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
            token = generate_token(user, operation=Operations.CONFIRM)
            # send_confirm_email(user, token)
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


@auth_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))

    if validate_token(user=current_user, token=token, operation=Operations.CONFIRM):
        flash('邮箱已激活', 'success')
        return redirect(url_for('main.index'))
    else:
        flash('邮箱激活失败', 'danger')
        return redirect(url_for('auth.resend_confirm_email'))


@auth_bp.route('/resend-confirm-email')
@login_required
def resend_confirm_email():
    if current_user.confirmed:
        return redirect(url_for('main.index'))

    token = generate_token(user=current_user, operation=Operations.CONFIRM)
    send_confirm_email(user=current_user, token=token)
    flash('新的验证邮件已发送，请查收', 'info')
    return redirect(url_for('user.index', username=current_user.username))


@auth_bp.route('/forget_password', methods=['POST', 'GET'])
def check_mail():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ForgetPasswordForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            return redirect(url_for('auth.reset_password', email=form.email.data))
        else:
            flash('邮箱不存在', 'warning')
    return render_template('auth/forget_password.html', form=form)


@auth_bp.route('/reset_password/<email>', methods=['POST', 'GET'])
def reset_password(email):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.query.filter_by(email=email).first()
    if user:
        form = ForgetPasswordResetForm()
        if form.validate_on_submit():
            if cache.get(user.username) == form.verify_code.data:
                user.set_password(form.password.data)
                db.session.commit()
                flash('密码找回成功!', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('验证码错误或失效', 'warning')
        return render_template('auth/forget_reset.html', form=form, email=email)
    else:
        abort(403)


@auth_bp.route('/send_verify_pwd/<email>')
def send_verify_pwd(email):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.query.filter_by(email=email).first()
    if user:
        if not cache.get(user.username + 'find'):
            token = random.randint(100000, 999999)
            send_token_email(user=user, token=token)
            cache.set(user.username, token, timeout=600)
            cache.set(user.username + 'find', 'true', timeout=45)
            return jsonify({'data': '邮件发送成功'})
        else:
            return jsonify({'data': 60})
    else:
        abort(403)
