# -*- coding: utf-8 -*-
import random
from flask import Blueprint, render_template, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user, logout_user

from MeiTu import User
from MeiTu.email_tool import send_token_email, send_change_email_email
from MeiTu.form.user import EditProfileForm, CropAvatarForm, UploadAvatarForm, ChangePasswordForm, ChangeEmailForm
from MeiTu.extensions import db, avatars, cache
from MeiTu.settings import Operations
from MeiTu.utils import redirect_back, generate_token, validate_token
from MeiTu.decorators import confirm_mail

user_bp = Blueprint('user', __name__)


@user_bp.route('/<username>')
@login_required
def index(username):
    return render_template('user/index.html')


@user_bp.route('/my_index/<username>')
@login_required
def my_index(username):
    user = User.query.filter_by(username=username).first_or_404()

    return render_template('user/my_index.html', user=user)


@user_bp.route('settings/profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.nick_name = form.nick_name.data
        current_user.location = form.location.data
        current_user.biography = form.biography.data
        db.session.commit()
        flash('个人信息修改成功！', 'success')
        return redirect(url_for('user.my_index', username=current_user.username))

    form.nick_name.data = current_user.nick_name
    form.biography.data = current_user.biography
    form.location.data = current_user.location
    return render_template('user/settings/edit_profile.html', form=form)


def flash_errors(form):
    pass


@user_bp.route('settings/avatar', methods=['POST', 'GET'])
@login_required
@confirm_mail
def change_avatar():
    upload_form = UploadAvatarForm()
    crop_form = CropAvatarForm()
    return render_template('user/settings/change_avatar.html', upload_form=upload_form, crop_form=crop_form)


@user_bp.route('/settings/avatar/upload', methods=['POST'])
@login_required
@confirm_mail
def upload_avatar():
    form = UploadAvatarForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = avatars.save_avatar(image)
        current_user.avatar_raw = filename
        try:
            db.session.commit()
            flash('图片上传成功！', 'success')
        except Exception as e:
            print('Exception:' + str(e))
            db.session.rollback()
    flash_errors(form)
    return redirect(url_for('user.change_avatar'))


@user_bp.route('/settings/avatar/crop', methods=['POST'])
@login_required
@confirm_mail
def crop_avatar():
    form = CropAvatarForm()
    if form.validate_on_submit():
        x = form.x.data
        y = form.y.data
        w = form.w.data
        h = form.h.data
        filenames = avatars.crop_avatar(current_user.avatar_raw, x, y, w, h)
        current_user.avatar_s = filenames[0]
        current_user.avatar_m = filenames[1]
        current_user.avatar_l = filenames[2]
        try:
            db.session.commit()
            flash('头像更新成功！', 'success')
        except Exception as e:
            print('Exception:' + str(e))
            db.session.rollback()
    flash_errors(form)
    return redirect(url_for('user.change_avatar'))


@user_bp.route('/settings/change-password', methods=['POST', 'GET'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.validate_password(form.old_password.data):
            if cache.get(current_user.username) == form.verify_code.data:
                current_user.set_password(form.password.data)
                db.session.commit()
                flash('修改成功,请重新登录', 'success')
                logout_user()
                return redirect(url_for('auth.login'))
            else:
                flash('验证码错误或失效', 'warning')
        else:
            flash('密码错误', 'warning')
    return render_template('user/settings/change_password.html', form=form)


@user_bp.route('/send_verify')
@login_required
def send_verify():
    if not cache.get(current_user.username + 'exist'):
        token = random.randint(100000, 999999)
        send_token_email(user=current_user, token=token)
        cache.set(current_user.username, token, timeout=600)
        cache.set(current_user.username + 'exist', 'true', timeout=45)
        return jsonify({'data': '邮件发送成功'})
    else:
        return jsonify({'data': 60})


@user_bp.route('/settings/change-email', methods=['POST', 'GET'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        token = generate_token(user=current_user, operation=Operations.CHANGE_EMAIL, new_email=form.email.data.lower())
        send_change_email_email(to=form.email.data, user=current_user, token=token)
        flash('重置链接已发送，请登录新邮箱查看', 'info')
        return redirect(url_for('user.index', username=current_user.username))
    return render_template('user/settings/change_email.html', form=form)


@user_bp.route('/email/confirm/<token>')
@login_required
def change_email_confirm(token):
    if validate_token(current_user, token, operation=Operations.CHANGE_EMAIL):
        flash('邮箱更改成功', 'success')
        return redirect(url_for('user.index', username=current_user.username))
    else:
        flash('邮箱更改失败，链接过期或失效。', 'warning')
        return redirect(url_for('user.change_email', username=current_user.username))
