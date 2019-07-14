# -*- coding: utf-8 -*-
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FileField, HiddenField, \
    IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, Optional, ValidationError
from MeiTu.models import User


class EditProfileForm(FlaskForm):
    nick_name = StringField('昵称', render_kw={'placeholder': '请输入昵称'}, validators=[DataRequired(), Length(1, 12)])
    location = StringField('城市', validators=[Optional(), Length(0, 50)])
    biography = TextAreaField('个人简介', validators=[Optional(), Length(0, 120)])
    submit = SubmitField('完成修改')


class UploadAvatarForm(FlaskForm):
    image = FileField('上传头像', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], '仅支持[ jpg, png]格式')
    ])
    submit = SubmitField('确认')


class CropAvatarForm(FlaskForm):
    x = HiddenField()
    y = HiddenField()
    w = HiddenField()
    h = HiddenField()
    submit = SubmitField('完成修改')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('再次输入', validators=[DataRequired()])
    verify_code = IntegerField('验证码', render_kw={'autocomplete': 'off'}, validators=[DataRequired()])
    submit = SubmitField('提交')


class ChangeEmailForm(FlaskForm):
    email = StringField('新的邮箱', validators=[DataRequired(), Length(1, 254), Email()])
    submit = SubmitField('更改')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('邮箱已经存在！')


class WriteTravelsForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 60)])
    body = CKEditorField('内容', validators=[DataRequired()])
    submit = SubmitField('完成')


class CommentForm(FlaskForm):
    body = TextAreaField('内容', validators=[DataRequired()])
    submit = SubmitField('发表评论')


class PrivacySettingForm(FlaskForm):
    public_collections = BooleanField('公开我的收藏')
    public_following = BooleanField('公开我的关注')
    public_followers = BooleanField('公开我的粉丝列表')
    submit = SubmitField('更改')


class TagForm(FlaskForm):
    tag = StringField('添加标签 (多个请用空格隔开)', validators=[Optional(), Length(0, 64)])
    submit = SubmitField('添加')


class NotificationSettingForm(FlaskForm):
    receive_comment_notification = BooleanField('新的回复')
    receive_follow_notification = BooleanField('新的关注')
    receive_collect_notification = BooleanField('新的收藏')
    submit = SubmitField('更改')
