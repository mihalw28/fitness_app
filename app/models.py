from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from flask import current_app



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    cell_number = db.Column(db.String(9), unique=True)
    club_site_login = db.Column(db.String(64))
    club_site_password = db.Column(db.String(128))
    #about_me = db.Column(db.String(140)) 
    club_name = db.Column(db.String(64))
    club_no = db.Column(db.Integer, unique=False)
    classes = db.Column(db.String(50))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow) # change to last visit in a gym :)
    activities = db.relationship('Activity', backref='author', lazy='dynamic')
    trainings = db.relationship('Train', backref='author', lazy='dynamic')


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
    
    def followed_trainings(self):
        own = Train.query.filter_by(user_id=self.id)
        return own.order_by(Train.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activ_body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Activity {}>'.format(self.body)

class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    your_training = db.Column(db.String(50))
    training_datetime = db.Column(db.DateTime, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    acceptance = db.Column(db.String(20), default='nie')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
     
    def __repr__(self):
        return '<Training {}>'.format(self.body)