import pytest
from flask import current_app

from app import create_app, db
from app.models import User
from config import Config


# TO DO: refactor config.py to get different configs for dev, prod and testing
# and finally remove this
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False


@pytest.fixture(scope="module")
def new_user():
    user = User(
        username="Mark",
        email="mark@orni.com",
        cell_number="123123123",
        club_site_login="salon@salon.com",
        club_site_password="dziK",
        club_name="Kino",
        club_no=1,
    )
    return user


@pytest.fixture(scope="module")  # socope="module" -> thanks to this, fixture invoked once per module
def app():
    app = create_app(TestConfig)
    with app.app_context():
        current_app.test_client()

        db.create_all()
        user1 = User(username="Keanu", email="keanu@reeves.com")
        user2 = User(username="Elon", email="elon@musk.com")
        user3 = User(username="micha", email="micha@micha.com")
        user3.set_password("micha")
        db.session.add_all([user1, user2, user3])
        db.session.commit()
        
        yield current_app
