# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
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
        if field.data != User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')
