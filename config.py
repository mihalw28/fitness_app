import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


def create_db_url(user, pw, host, dbname):
    return f"postgresql+psycopg2://{user}:{pw}@{host}:5432/{dbname}"


def get_env_db_url(env_setting):
    if env_setting == "development":
        return f"sqlite:///{os.path.join(basedir, 'app.db')}"
    elif env_setting == "testing":
        PSQL_USER = os.environ["PSQL_USER"]
        PSQL_PW = os.environ["PSQL_PW"]
        PSQL_DB = os.environ["PSQL_DB"]
        PSQL_HOST = os.environ["PSQL_HOST"]
    elif env_setting == "production":
        PSQL_USER = os.environ["PSQL_USERs"]
        PSQL_PW = os.environ["PSQL_PWs"]
        PSQL_DB = os.environ["PSQL_DBs"]
        PSQL_HOST = os.environ["PSQL_HOSTs"]

    return create_db_url(PSQL_USER, PSQL_PW, PSQL_HOST, PSQL_DB)


# SET database urls for every environment
DEV_DB_URL = get_env_db_url("development")
TESTING_DB_URL = get_env_db_url("testing")
PROD_DB_URL = get_env_db_url("production")


class Config(object):
    SECRET_KEY = os.environ["SECRET_KEY"] or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = DEV_DB_URL
    # SQLALCHEMY_DATABASE_URI = os.environ.get(
    #     "DATABASE_URL"
    # ) or "sqlite:///" + os.path.join(basedir, "app.db")
    # PSQL_USER = os.environ["PSQL_USER"]
    # PSQL_PW = os.environ["PSQL_PW"]
    # PSQL_DB = os.environ["PSQL_DB"]
    # PSQL_HOST = os.environ["PSQL_HOST"]
    # SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{user}:{pw}@{host}:5432/{dbname}".format(
    #     user=PSQL_USER, pw=PSQL_PW, host=PSQL_HOST, dbname=PSQL_DB
    # )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ["MAIL_SERVER"]
    MAIL_PORT = int(os.environ["MAIL_PORT"] or 25)
    MAIL_USE_TLS = os.environ["MAIL_USE_TLS"] is not None
    MAIL_USERNAME = os.environ["MAIL_USERNAME"]
    MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
    ADMINS = ["mihalw28@o2.pl"]
    ACTIVITIES_PER_PAGE = 8
    GYM_LOGIN_URL = os.environ["GYM_LOGIN_URL"]
    GYM_LIST_CLASSES = os.environ["GYM_LIST_CLASSES"]
    TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID_TEMP"]
    TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN_TEMP"]
    TWILIO_PHONE_NUMBER = os.environ["TWILIO_PHONE_NUMBER"]
    SCHEDULER_API_ENABLED = True
    KEY = os.environ["KEY"]
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = TESTING_DB_URL
    TESTING = True


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = PROD_DB_URL
    DEBUG = False
    TESTING = False
