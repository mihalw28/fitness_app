from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import User, Train
from config import Config
import pytest
#from flask import url_for
#import flask_testing
#from flask_testing import TestCase

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        #self.app = self.app.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='sam')
        u.set_password('mas')
        self.assertFalse(u.check_password('sma'))
        self.assertTrue(u.check_password('mas'))

    def test_avatar(self):
        u = User(username='elon', email='elon@musk.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'e7959a50c2ef77c47391d53933b383c2'
                                         '?d=retro&s=128'))

    def test_cell_number(self): # think it is something wrong here
        u = User(username='michal', cell_number='48509590590')
        self.assertNotEqual(u.cell_number, ('48590390590'))

    def test_follow_activities(self):
        #create 2 users
        u1 = User(username='sam', email='sam@example.com')
        u2 = User(username='magi', email='magi@example.com')
        db.session.add_all([u1, u2])

        #create 2 trainings
        now = datetime.utcnow()
        t1 = Train(your_training='Yoga', athlete=u1, timestamp=now + timedelta(seconds=1))
        t2 = Train(your_training='Bodypump', athlete=u2, timestamp=now + timedelta(seconds=2))
        db.session.add_all([t1, t2])
        db.session.commit()

        #check followed activities
        f1 = u1.followed_trainings().all()
        f2 = u2.followed_trainings().all()
        self.assertEqual(f1, [t1])
        self.assertEqual(f2, [t2])

    def test_user_model(self):
        """
        Test number of in User table
        """
        u1 = User(username='sam', email='sam@example.com')
        u2 = User(username='magi', email='magi@example.com')
        u3 = User(username='micha', email='micha@micha.com')
        db.session.add_all([u1, u2, u3])
        db.session.commit()
        self.assertEqual(User.query.count(), 3)

    def test_train_model(self):
        """
        Test number of records in Train table
        """
        # create test trainings
        t1 = Train(your_training='Yoga')
        t2 = Train(your_training='Bodypump')
        t3 = Train(your_training='Yoga')
        t4 = Train(your_training='Bodypump')
        t5 = Train(your_training='Yoga')
        t6 = Train(your_training='Bodypump')

        # save department to database
        db.session.add_all([t1, t2, t3, t4, t5, t6])
        db.session.commit()
        self.assertEqual(Train.query.count(), 6)

if __name__ == '__main__':
    unittest.main(verbosity=2)