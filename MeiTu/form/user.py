# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FileField, HiddenField, \
    IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, Optional, ValidationError
from MeiTu.models import User


class EditProfileForm(FlaskForm):
    username = StringField('用户名', render_kw={'placeholder': '请输入用户名'}, validators=[DataRequired(), Length(1, 12),
                                                                                   Regexp('^[a-zA-Z][a-zA-Z0-9]*$',
                                                                                          message='请输入以字母开头，数字与字母的组合')])
    nick_name = StringField('昵称', render_kw={'placeholder': '请输入昵称'}, validators=[DataRequired(), Length(1, 12)])
    location = StringField('城市', validators=[Optional(), Length(0, 50)])
    biography = TextAreaField('个人简介', validators=[Optional(), Length(0, 120)])
    submit = SubmitField('完成修改')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')


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
