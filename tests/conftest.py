import pytest
from app import create_app, db
from app.models import Train, User
from config import Config
from flask import current_app


# TO DO: refactor config.py to get different configs for dev, prod and testing
# and finally remove this
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


@pytest.fixture(scope="module")
def new_user():
    user = User(
        username="Mark",
        email="mark@orni.com",
        password_hash="milargo",
        cell_number="123123123",
        club_site_login="salon",
        club_site_password="orange",
        club_name="Kino",
        club_no=1,
    )
    return user


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    # testing_client = app.test_client()
    # ctx = app.app_context()
    # ctx.push()
    # yield testing_client
    # ctx.pop()
    with app.app_context():
        current_app.test_client()
    return app


@pytest.fixture()
def init_db():
    db.create_all()
    user1 = User(username="Keanu", email="keanu@reeves.com")
    user2 = User(username="Elon", email="elon@musk.com")
    user3 = User(username="micha", email="micha@micha.com")
    db.session.add_all([user1, user2, user3])
    db.session.commit()
    yield db
    db.drop_all()
