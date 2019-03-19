# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp


class LoginForm(FlaskForm):
    email = StringField('邮箱', render_kw={'placeholder': '您的邮箱'}, validators=[DataRequired(), Length(1, 254), Email()])
    password = PasswordField('密码', render_kw={'placeholder': '您的密码'}, validators=[DataRequired()])
    remember_me = BooleanField('七天免登陆')
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    username = StringField('用户名', render_kw={'placeholder': '请输入用户名'}, validators=[DataRequired(), Length(1, 20),
                                                                                   Regexp('^[a-zA-Z][a-zA-Z0-9]*$',
                                                                                          message='请输入以字母开头，数字与字母的组合')])
    password = PasswordField('密码', render_kw={'placeholder': '请输入密码'},
                             validators=[DataRequired(), Length(1, 128), EqualTo('password2', message='两次密码不一致')])
    password2 = PasswordField('确认密码', render_kw={'placeholder': '请再次输入密码'}, validators=[DataRequired()])
    email = StringField('Email', render_kw={'placeholder': '您的邮箱'}, validators=[DataRequired(), Length(1, 254), Email()])
    nick_name = StringField('昵称', render_kw={'placeholder': '请输入昵称'}, validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField('立即注册')
