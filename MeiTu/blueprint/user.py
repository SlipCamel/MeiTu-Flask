# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from MeiTu.form.user import EditProfileForm
from MeiTu.extensions import db
from MeiTu.utils import redirect_back

user_bp = Blueprint('user', __name__)


@user_bp.route('/<username>')
@login_required
def index(username):
    return render_template('user/index.html')


@user_bp.route('settings/profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.nick_name = form.nick_name.data
        current_user.location = form.location.data
        current_user.biography = form.biography.data
        db.session.commit()
        flash('个人信息修改成功！', 'success')
        # 应返回个人信息页，目前未完成顾返回个人首页
        return redirect(url_for('user.index', username=current_user.username))

    form.username.data = current_user.username
    form.nick_name.data = current_user.nick_name
    form.biography.data = current_user.biography
    form.location.data = current_user.location
    return render_template('user/settings/edit_profile.html', form=form)
