import unittest
from datetime import datetime, timedelta

from flask import abort, current_app, url_for
from flask_testing import TestCase

from app import create_app, db
from app.models import Train, User
from config import Config
from app.auth.crypting import decrypt_gym_password
# import sqlite3


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


class TestBase(TestCase):
    def create_app(self):
        app = create_app(TestConfig)
        with app.app_context():
            # client = current_app.test_client()
            current_app.test_client()
        return app

    def setUp(self):
        db.session.commit()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestModels(TestBase):
    def test_password_hashing(self):
        u = User(username="sam")
        u.set_password("mas")
        self.assertFalse(u.check_password("sma"))
        self.assertTrue(u.check_password("mas"))

    def test_avatar(self):
        u = User(username="elon", email="elon@musk.com")
        self.assertEqual(
            u.avatar(128),
            (
                "https://www.gravatar.com/avatar/"
                "e7959a50c2ef77c47391d53933b383c2"
                "?d=retro&s=128"
            ),
        )

    def test_cell_number(self):  # think it is something wrong here
        u = User(username="michal", cell_number="48509590590")
        self.assertNotEqual(u.cell_number, ("48590390590"))

    def test_follow_activities(self):
        # create 2 users
        u1 = User(username="sam", email="sam@example.com")
        u2 = User(username="magi", email="magi@example.com")
        db.session.add_all([u1, u2])

        # create 2 trainings
        now = datetime.utcnow()
        t1 = Train(
            your_training="Yoga", athlete=u1, timestamp=now + timedelta(seconds=1)
        )
        t2 = Train(
            your_training="Bodypump", athlete=u2, timestamp=now + timedelta(seconds=2)
        )
        db.session.add_all([t1, t2])
        db.session.commit()

        # check followed activities
        f1 = u1.followed_trainings().all()
        f2 = u2.followed_trainings().all()
        self.assertEqual(f1, [t1])
        self.assertEqual(f2, [t2])

    def test_user_model(self):
        """
        Test number of in User table
        """
        u1 = User(username="sam", email="sam@example.com")
        u2 = User(username="magi", email="magi@example.com")
        u3 = User(username="micha", email="micha@micha.com")
        db.session.add_all([u1, u2, u3])
        db.session.commit()
        self.assertEqual(User.query.count(), 3)

    def test_train_model(self):
        """
        Test number of records in Train table
        """
        # create test trainings
        t1 = Train(your_training="Yoga")
        t2 = Train(your_training="Bodypump")
        t3 = Train(your_training="Yoga")
        t4 = Train(your_training="Bodypump")
        t5 = Train(your_training="Yoga")
        t6 = Train(your_training="Bodypump")

        # save department to database
        db.session.add_all([t1, t2, t3, t4, t5, t6])
        db.session.commit()
        self.assertEqual(Train.query.count(), 6)

    def test_gym_site_pasword_encryption(self):
        """
        Test password encryption and decrytpion
        """
        u1 = User(username="kali", club_site_password="kamikadze")
        u1.encrypt_site_password("kamikadze")
        db.session.add_all([u1])
        db.session.commit()
        u = User.query.first()
        plain_text_password = decrypt_gym_password(u)
        self.assertEqual(plain_text_password, 'kamikadze')


class TestViews(TestBase):
    def test_login_view(self):
        """
        Test that login page is accessible without login
        """
        # with current_app.app_context():
        response = self.client.get(url_for("auth.login"))
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        """
        Test inaccessibility of logout link without login
        """
        target_url = url_for("auth.logout")
        redirect_url = url_for("auth.login", next=target_url)
        # with current_app.app_context():
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_home_page(self):
        """
        Test that dashboard is inaccessible without login
        and redirects to login page then to dashboard
        """
        target_url = url_for("main.index")
        redirect_url = url_for("auth.login", next=target_url)
        # with current_app.app_context():
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_profile_view(self):
        """
        Test user profile inaccessibility without login
        and redirects to login page then to profile page
        """
        target_url = url_for("main.user", username="Verylongname")
        redirect_url = url_for("auth.login", next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_edit_profile_view(self):
        """
        Test user edit_profile inaccessibility without login
        and redirects to login page then to profile page
        """
        target_url = url_for("main.edit_profile")
        redirect_url = url_for("auth.login", next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)


class TestErrors(TestBase):
    def test_not_found_error(self):
        response = self.client.get("/errors/404")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(b"File Not Found" in response.data)

    def test_internal_error(self):
        # create route to abort the request with the 500 Error
        @self.app.route("/errors/500")
        def internal_error():
            abort(500)

        response = self.client.get("/errors/500")
        self.assertEqual(response.status_code, 500)
        # There isn't any option of typing b"foo" below, because of ASCII
        # literal characters (presence of polish letters)
        self.assertTrue("nieprzewidziany błąd" in response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
