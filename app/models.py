from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login
from flask_login import UserMixin
from hashlib import md5

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    cell_number = db.Column(db.BIGINT)
    club_site_login = db.Column(db.String(64))
    club_site_password = db.Column(db.String(128))
    activities = db.relationship('Activity', backref='person', lazy='dynamic')
    about_me = db.Column(db.String(140)) 
    last_seen = db.Column(db.DateTime, default=datetime.utcnow) # change to last visit in a gym :)
    


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=retro&s={}'.format(
            digest, size)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.String(64))
    club_no = db.Column(db.Integer, unique=False)
    pref_activity = db.Column(db.String(64), unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Activity {}>'.format(self.body)