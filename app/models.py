from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from app import db, login
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from flask import current_app
from flask import url_for
import base64
import os


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class User(PaginatedAPIMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    cell_number = db.Column(db.String(9), unique=True)
    club_site_login = db.Column(db.String(64))
    club_site_password = db.Column(db.String(128))
    club_name = db.Column(db.String(64))
    club_no = db.Column(db.Integer, unique=False)
    classes = db.Column(db.String(50))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)  # change to last visit
    trainings = db.relationship('Train', backref='athlete', lazy='dynamic')
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=retro&s={size}'

    def followed_trainings(self):
        own = Train.query.filter_by(user_id=self.id)
        return own.order_by(Train.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},
                          current_app.config['SECRET_KEY'],
                          algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.isoformat() + 'Z',
            'cell_number': self.cell_number,
            'club_site_login': self.club_site_login,
            'club_site_password': self.club_site_password,
            'club_name': self.club_name,
            'club_no': self.club_no,
            'classes': self.classes,
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'trainings': url_for('api.get_user_trainings', id=self.id),
                'avatar': self.avatar(128)
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'cell_number', 'club_name',
                      'club_no', 'classes']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Train(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    your_training = db.Column(db.String(50))
    training_datetime = db.Column(db.DateTime, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    acceptance = db.Column(db.String(20), default='nie')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Training {self.your_training}>'

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'your_training': self.your_training,
            'training_datetime': self.training_datetime,
            'acceptance': self.acceptance,
            '_links': {
                'self': url_for('api.get_user_trainings', id=self.id)
            }
        }
        return data


"""
    def trainings_from_dict(self, data, new_user=False):
        for field in ['username', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])
"""
