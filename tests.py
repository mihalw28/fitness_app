from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Activity

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://' # db for testing
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

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
        u1 = User(username='sam', email='sam@example.com')
        u2 = User(username='magi', email='magi@example.com')
        db.session.add_all([u1, u2])

        #create 2 activities
        now = datetime.utcnow()
        a1 = Activity(activ_body='yoga', author=u1, timestamp=now + timedelta(seconds=1))
        a2 = Activity(activ_body='bodypump', author=u2, timestamp=now + timedelta(seconds=2))
        db.session.add_all([a1, a2])
        db.session.commit()

        #check the followed activities
        f1 = u1.followed_activities().all()
        f2 = u2.followed_activities().all()
        self.assertEqual(f1, [a1])
        self.assertEqual(f2, [a2])

if __name__ == '__main__':
    unittest.main(verbosity=2)