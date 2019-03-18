# -*- coding: utf-8 -*-
from flask import Blueprint, render_template
from MeiTu.form.auth import LoginForm
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('MeiTu/login.html',  form=form)
