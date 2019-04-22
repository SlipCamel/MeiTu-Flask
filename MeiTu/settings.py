# -*- coding: utf-8 -*-
import os
import sys

from flask_login import current_user

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
    # SQLALCHEMY_ECHO = True

    CACHE_TYPE = 'redis'
    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 1

    MEITU_UPLOAD_PATH = os.path.join(basedir, 'uploads')
    MEITU_MAIL_SUBJECT_PREFIX = '[美途]'
    MEITU_TRAVELS_PER_PAGE = 10
    MEITU_TRAVELS_USER_PER_PAGE = 9
    MEITU_MANAGE_COMMENT_PER_PAGE = 30
    MEITU_MANAGE_TAG_PER_PAGE = 50
    MEITU_NOTIFICATION_PER_PAGE = 20

    AVATARS_SAVE_PATH = os.path.join(MEITU_UPLOAD_PATH, 'avatars')
    AVATARS_SIZE_TUPLE = (30, 100, 200)

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('美途-管理员', MAIL_USERNAME)

    DROPZONE_ALLOWED_FILE_TYPE = 'image'
    DROPZONE_MAX_FILE_SIZE = 5
    DROPZONE_MAX_FILES = 1
    DROPZONE_ENABLE_CSRF = True
    DROPZONE_DEFAULT_MESSAGE = '请上传一张游记头图，图片大小小于5MB。'
    DROPZONE_FILE_UPLOAD = os.path.join(MEITU_UPLOAD_PATH, 'head')

    CKEDITOR_ENABLE_CSRF = True
    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_FILE_UPLOADER = '/user/upload'
    CKEDITOR_FILE_BROWSER = '/user/show_upload'
    FILE_UPLOAD = os.path.join(MEITU_UPLOAD_PATH, 'pic')


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')


class ProductionConfig(BaseConfig):
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
