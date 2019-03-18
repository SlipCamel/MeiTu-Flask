# -*- coding: utf-8 -*-
from flask import Blueprint, render_template
from MeiTu.form.auth import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    return render_template('auth/register.html', form=form)
