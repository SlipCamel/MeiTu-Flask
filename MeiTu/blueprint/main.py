# -*- coding: utf-8 -*-
import os

from flask import Blueprint, render_template, current_app, send_from_directory, request, flash
from sqlalchemy import func

from MeiTu.form.user import CommentForm, TagForm
from MeiTu.models import Travels, Comment, Collect, User, Tag
from MeiTu.utils import redirect_back

main_bp = Blueprint('main', __name__)


@main_bp.route('/', defaults={'order': 'by_collectors'})
@main_bp.route('/<order>')
def index(order):
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_TRAVELS_PER_PAGE']
    pagination = Travels.query.paginate(page, per_page=per_page)
    travels = pagination.items
    travels.sort(key=lambda x: len(x.collectors), reverse=True)

    if order == 'by_time':
        pagination = Travels.query.order_by(Travels.timestamp.desc()).paginate(page, per_page=per_page)
        travels = pagination.items
    tags = Tag.query.join(Tag.travels).group_by(Tag.id).order_by(func.count(Travels.id).desc()).limit(10).all()
    return render_template('main/index.html', pagination=pagination, travels=travels, length=len, tags=tags,
                           order=order)


@main_bp.route('/travel/<int:travel_id>')
def show_travels(travel_id):
    travel = Travels.query.get_or_404(travel_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_TRAVELS_PER_PAGE']
    pagination = Comment.query.with_parent(travel).order_by(Comment.timestamp.asc()).paginate(page, per_page)
    comments = pagination.items

    comment_form = CommentForm()
    tag_form = TagForm()

    return render_template('main/travel.html', travel=travel, pagination=pagination, comments=comments,
                           comment_form=comment_form, tag_form=tag_form)


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


@main_bp.route('/<username>/following')
def show_following(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_TRAVELS_PER_PAGE']
    pagination = user.following.paginate(page, per_page)
    follows = pagination.items
    return render_template('main/show_following.html', user=user, pagination=pagination, follows=follows)


@main_bp.route('/<username>/followers')
def show_followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_TRAVELS_PER_PAGE']
    pagination = user.followers.paginate(page, per_page)
    follows = pagination.items
    return render_template('main/show_followers.html', user=user, pagination=pagination, follows=follows)


@main_bp.route('/tag/<int:tag_id>', defaults={'order': 'by_time'})
@main_bp.route('/tag/<int:tag_id>/<order>')
def show_tag(tag_id, order):
    tag = Tag.query.get_or_404(tag_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_TRAVELS_USER_PER_PAGE']
    order_rule = 'time'
    pagination = Travels.query.with_parent(tag).order_by(Travels.timestamp.desc()).paginate(page, per_page)
    travels = pagination.items

    if order == 'by_collects':
        travels.sort(key=lambda x: len(x.collectors), reverse=True)
        order_rule = 'collects'
    return render_template('main/show_tag.html', tag=tag, pagination=pagination, travels=travels, order_rule=order_rule)


@main_bp.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)


@main_bp.route('/search')
def search():
    q = request.args.get('q', '')
    if q == '':
        flash('请输入查询信息', 'warning')
        return redirect_back()

    order_rule = request.args.get('order_rule', 'search_travels')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_TRAVELS_USER_PER_PAGE']
    if order_rule == 'search_travels':
        pagination = Travels.query.whooshee_search(q).paginate(page, per_page)
        order_rule = 'search_travels'
    elif order_rule == 'search_users':
        pagination = User.query.whooshee_search(q).paginate(page, per_page)
        order_rule = 'search_users'
    else:
        pagination = Tag.query.whooshee_search(q).paginate(page, per_page)
        order_rule = 'search_tags'
    results = pagination.items

    return render_template('main/search.html', results=results, pagination=pagination, order_rule=order_rule, q=q)
