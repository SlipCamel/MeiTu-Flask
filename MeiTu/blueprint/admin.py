from flask import render_template, flash, Blueprint, request, current_app
from flask_login import login_required, current_user

from MeiTu import db
from MeiTu.models import User, Travels, Tag, Comment
from MeiTu.utils import redirect_back
from MeiTu.decorators import admin_required
from MeiTu.notifications import push_delete_notification

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@login_required
@admin_required
def index():
    user_count = User.query.count()
    travel_count = Travels.query.count()
    tag_count = Tag.query.count()
    comment_count = Comment.query.count()
    return render_template('admin/index.html', user_count=user_count, travel_count=travel_count, tag_count=tag_count,
                           comment_count=comment_count)


@admin_bp.route('/manage/comment')
@login_required
@admin_required
def manage_comment():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_MANAGE_COMMENT_PER_PAGE']
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page, per_page)

    comments = pagination.items
    return render_template('admin/manage_comment.html', pagination=pagination, comments=comments)


@admin_bp.route('/manage/tag')
@login_required
@admin_required
def manage_tag():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_MANAGE_TAG_PER_PAGE']
    pagination = Tag.query.paginate(page, per_page)
    tags = pagination.items
    return render_template('admin/manage_tag.html', pagination=pagination, tags=tags)


@admin_bp.route('/delete/tag/<int:tag_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash('Tag deleted.', 'info')
    return redirect_back()


@admin_bp.route('/manage/user')
@login_required
@admin_required
def manage_user():
    filter_rule = request.args.get('filter', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_MANAGE_TAG_PER_PAGE']

    if filter_rule == 'locked':
        filtered_users = User.query.filter_by(active=False)
    elif filter_rule == 'administrator':
        filtered_users = User.query.filter_by(is_admin=True)
    else:
        filtered_users = User.query

    pagination = filtered_users.order_by(User.member_since.desc()).paginate(page, per_page)
    users = pagination.items
    return render_template('admin/manage_user.html', pagination=pagination, users=users)


@admin_bp.route('/unlock/user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def unlock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.unlock()
    flash('用户已解锁', 'info')
    return redirect_back()


@admin_bp.route('/lock/user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def lock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.lock()
    flash('用户已封禁', 'info')
    return redirect_back()


@admin_bp.route('/manage/travel')
@login_required
@admin_required
def manage_travel():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_MANAGE_TAG_PER_PAGE']
    pagination = Travels.query.order_by(Travels.timestamp.desc()).paginate(page, per_page)
    travels = pagination.items
    return render_template('admin/manage_travel.html', travels=travels, pagination=pagination)


@admin_bp.route('/delete/travel/<int:travel_id>', methods=['POST'])
@login_required
@admin_required
def delete_travel(travel_id):
    travel = Travels.query.get_or_404(travel_id)
    db.session.delete(travel)
    db.session.commit()
    flash('游记已删除', 'info')
    push_delete_notification(current_user, travel)
    return redirect_back()
