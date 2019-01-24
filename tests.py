from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User

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

if __name__ == '__main__':
    unittest.main(verbosity=2)