# -*- coding: utf-8 -*-
from flask import current_app, request, url_for, redirect, flash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from MeiTu.settings import Operations
from MeiTu.extensions import db

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='main.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def generate_token(user, operation, expire_in=None, **kwargs):
    """
    :param user: user object instance
    :param operation: Operational variables. include：confirm、reset-password、change-email
    :param expire_in: Token expiration time. default 3600s
    :return: confirm-token(JWS)
    """

    s = Serializer(current_app.config['SECRET_KEY'], expire_in)
    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    # return s.dumps(data)
    return str(s.dumps(data), 'utf-8')


def validate_token(user, token, operation):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature) as e:
        print(str(e))
        return False

    if user.id != data.get('id') or operation != data.get('operation'):
        return False

    if operation == Operations.CONFIRM:
        user.confirmed = True
        db.session.commit()

    return True
