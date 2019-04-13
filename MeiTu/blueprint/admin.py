from flask import render_template, flash, Blueprint, request, current_app
from flask_login import login_required

from MeiTu import db
from MeiTu.models import User, Travels, Tag, Comment
from MeiTu.utils import redirect_back

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
def index():
    user_count = User.query.count()
    travel_count = Travels.query.count()
    tag_count = Tag.query.count()
    comment_count = Comment.query.count()
    return render_template('admin/index.html', user_count=user_count, travel_count=travel_count, tag_count=tag_count,
                           comment_count=comment_count)


@admin_bp.route('/manage/comment')
@login_required
def manage_comment():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_MANAGE_COMMENT_PER_PAGE']
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page, per_page)

    comments = pagination.items
    return render_template('admin/manage_comment.html', pagination=pagination, comments=comments)


@admin_bp.route('/manage/tag')
@login_required
def manage_tag():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MEITU_MANAGE_TAG_PER_PAGE']
    pagination = Tag.query.paginate(page, per_page)
    tags = pagination.items
    return render_template('admin/manage_tag.html', pagination=pagination, tags=tags)


@admin_bp.route('/delete/tag/<int:tag_id>', methods=['GET', 'POST'])
@login_required
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash('Tag deleted.', 'info')
    return redirect_back()
