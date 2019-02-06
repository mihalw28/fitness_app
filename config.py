import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['mihalw28@o2.pl']
    ACTIVITIES_PER_PAGE = 8
    #GYM_USER_NAME = os.environ.get('GYM_USER_NAME')
    #GYM_USER_PASSWORD = os.environ.get('GYM_USER_PASSWORD')
    GYM_LOGIN_URL = os.environ.get('GYM_LOGIN_URL')
    GYM_LIST_CLASSES = os.environ.get('GYM_LIST_CLASSES')