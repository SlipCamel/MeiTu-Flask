# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp


class LoginForm(FlaskForm):
    email = StringField('邮箱', render_kw={'placeholder': '您的邮箱', }, validators=[DataRequired(), Length(1, 254), Email()])
    password = PasswordField('密码', render_kw={'placeholder': '您的密码', }, validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')
