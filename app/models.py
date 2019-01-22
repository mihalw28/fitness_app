from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    cell_number = db.Column(db.BIGINT)
    club_site_login = db.Column(db.String(64))
    club_site_password = db.Column(db.String(128))
    activities = db.relationship('Activity', backref='person', lazy='dynamic')


    def __repr__(self):
        return '<User {}>'.format(self.username)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.String(64))
    club_no = db.Column(db.Integer, unique=False)
    pref_activity = db.Column(db.String(64), unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Activity {}>'.format(self.body)