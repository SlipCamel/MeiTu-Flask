from flask import render_template, Blueprint, jsonify
from flask_login import current_user

from MeiTu import User
from MeiTu.models import Notification
from MeiTu.notifications import push_follow_notification

ajax_bp = Blueprint('ajax', __name__)


@ajax_bp.route('/profile/<int:user_id>')
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('main/profile_popup.html', user=user)


@ajax_bp.route('/followers-count/<int:user_id>')
def followers_count(user_id):
    user = User.query.get_or_404(user_id)
    count = user.followers.count() - 1  # minus user self
    return jsonify(count=count)


@ajax_bp.route('/unfollow/<username>', methods=['POST'])
def unfollow(username):
    if not current_user.is_authenticated:
        return jsonify(message='请登录'), 403

    user = User.query.filter_by(username=username).first_or_404()
    if not current_user.is_following(user):
        return jsonify(message='还未关注'), 400

    current_user.unfollow(user)
    return jsonify(message='取消关注成功')


@ajax_bp.route('/follow/<username>', methods=['POST'])
def follow(username):
    if not current_user.is_authenticated:
        return jsonify(message='请登录'), 403
    elif not current_user.confirmed:
        return jsonify(message='请先验证邮箱'), 400

    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        return jsonify(message='已经关注'), 400

    current_user.follow(user)
    if user.receive_follow_notification:
        push_follow_notification(follower=current_user, receiver=user)
    return jsonify(message='关注成功')


@ajax_bp.route('/notifications-count')
def notifications_count():
    if not current_user.is_authenticated:
        return jsonify(message='请登录'), 403

    count = Notification.query.with_parent(current_user).filter_by(is_read=False).count()
    return jsonify(count=count)
