import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
<<<<<<< Updated upstream
    SECRET_KEY = os.environ['SECRET_KEY'] or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #    'sqlite:///' + os.path.join(basedir, 'app.db')
    PSQL_USER = os.environ['PSQL_USER']
    PSQL_PW = os.environ['PSQL_PW']
    PSQL_DB = os.environ['PSQL_DB']
    PSQL_HOST = os.environ['PSQL_HOST']
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{user}:{pw}@{host}:5432/{dbname}".\
        format(user=PSQL_USER, pw=PSQL_PW, host=PSQL_HOST, dbname=PSQL_DB)
=======
    SECRET_KEY = os.environ["SECRET_KEY"] or "you-will-never-guess"
    # SQLALCHEMY_DATABASE_URI = os.environ.get(
    #     "DATABASE_URL"
    # ) or "sqlite:///" + os.path.join(basedir, "app.db")
    PSQL_USER = os.environ["PSQL_USER"]
    PSQL_PW = os.environ["PSQL_PW"]
    PSQL_DB = os.environ["PSQL_DB"]
    PSQL_HOST = os.environ["PSQL_HOST"]
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{user}:{pw}@{host}:5432/{dbname}".format(
        user=PSQL_USER, pw=PSQL_PW, host=PSQL_HOST, dbname=PSQL_DB
    )
>>>>>>> Stashed changes
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ['MAIL_SERVER']
    MAIL_PORT = int(os.environ['MAIL_PORT'] or 25)
    MAIL_USE_TLS = os.environ['MAIL_USE_TLS'] is not None
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    ADMINS = ['mihalw28@o2.pl']
    ACTIVITIES_PER_PAGE = 8
    GYM_LOGIN_URL = os.environ['GYM_LOGIN_URL']
    GYM_LIST_CLASSES = os.environ['GYM_LIST_CLASSES']
    TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID_TEMP']
    TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN_TEMP']
    SCHEDULER_API_ENABLED = True
<<<<<<< Updated upstream
    TWILIO_PHONE_NUMBER = os.environ['TWILIO_PHONE_NUMBER']
=======
    TWILIO_PHONE_NUMBER = os.environ["TWILIO_PHONE_NUMBER"]
    HASH_KEY = os.environ["HASH_KEY"]
>>>>>>> Stashed changes
