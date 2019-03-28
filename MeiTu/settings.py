# -*- coding: utf-8 -*-
import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class Operations:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-email'


class BaseConfig(object):
    SECRET_KEY = 'D6Z8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = 'redis'
    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 1

    MEITU_UPLOAD_PATH = os.path.join(basedir, 'uploads')
    MEITU_MAIL_SUBJECT_PREFIX = '[美途]'

    AVATARS_SAVE_PATH = os.path.join(MEITU_UPLOAD_PATH, 'avatars')
    AVATARS_SIZE_TUPLE = (30, 100, 200)

    MAX_CONTENT_LENGTH = 3 * 1024 * 1024

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('美途-管理员', MAIL_USERNAME)


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')


class ProductionConfig(BaseConfig):
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
