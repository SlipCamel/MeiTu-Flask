# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, current_app, send_from_directory, request

from MeiTu.form.user import CommentForm
from MeiTu.models import Travels, Comment, Collect, User

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_TRAVELS_PER_PAGE']
    pagination = Travels.query.paginate(page, per_page=per_page)
    travels = pagination.items
    return render_template('main/index.html', pagination=pagination, travels=travels, length=len)


@main_bp.route('/travel/<int:travel_id>')
def show_travels(travel_id):
    travel = Travels.query.get_or_404(travel_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_TRAVELS_PER_PAGE']
    pagination = Comment.query.with_parent(travel).order_by(Comment.timestamp.asc()).paginate(page, per_page)
    comments = pagination.items

    comment_form = CommentForm()

    return render_template('main/travel.html', travel=travel, pagination=pagination, comments=comments,
                           comment_form=comment_form)


@main_bp.route('/travel/<int:travel_id>/collectors')
def show_collectors(travel_id):
    travel = Travels.query.get_or_404(travel_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_TRAVELS_PER_PAGE']
    pagination = Collect.query.with_parent(travel).order_by(Collect.timestamp.asc()).paginate(page, per_page)
    collects = pagination.items
    return render_template('main/collectors.html', collects=collects, travel=travel, pagination=pagination)


@main_bp.route('/<username>/collections')
def show_collections(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_TRAVELS_USER_PER_PAGE']
    pagination = Collect.query.with_parent(user).order_by(Collect.timestamp.desc()).paginate(page, per_page)
    collects = pagination.items
    return render_template('main/show_collections.html', collects=collects, pagination=pagination, user=user)


@main_bp.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)
