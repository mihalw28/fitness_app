import base64
import os
from datetime import datetime, timedelta
from hashlib import md5
from time import time

import jwt
from cryptography.fernet import Fernet
from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


class PaginatedAPIMixin(object):
    # credits to Miguel Grinberg for this class
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            "items": [item.to_dict() for item in resources.items],
            "_meta": {
                "page": page,
                "per_page": per_page,
                "total_pages": resources.pages,
                "total_items": resources.total,
            },
            "_links": {
                "self": url_for(endpoint, page=page, per_page=per_page, **kwargs),
                "next": url_for(endpoint, page=page + 1, per_page=per_page, **kwargs)
                if resources.has_next
                else None,
                "prev": url_for(endpoint, page=page - 1, per_page=per_page, **kwargs)
                if resources.has_prev
                else None,
            },
        }
        return data


class User(PaginatedAPIMixin, UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    cell_number = db.Column(db.String(9), unique=True)
    club_site_login = db.Column(db.String(64))
    club_site_password = db.Column(db.String(512))
    club_name = db.Column(db.String(64))
    club_no = db.Column(db.Integer, unique=False)
    classes = db.Column(db.String(50))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)  # change to last visit
    trainings = db.relationship("Train", backref="athlete", lazy="dynamic")
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def encrypt_site_password(self, gym_password):
        """Gets plain text user's gym site password, ecryptes it and
        changes it's binary form to "utf-8" format to save in db.

        Args:
            gym_password (str): Plain text gym_password
            key (string): Bytes from env string variable
        """
        # Change gym password from plain string to binary
        b_gym_password = gym_password.encode()
        f = Fernet(current_app.config["KEY"])
        # Generate encrypted password
        encrypted_password = f.encrypt(b_gym_password)
        # Decode password to plain text
        plain_encrypted_password = bytes(encrypted_password).decode("utf-8")
        self.club_site_password = plain_encrypted_password

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=retro&s={size}"

    def followed_trainings(self):
        own = Train.query.filter_by(user_id=self.id)
        return own.order_by(Train.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        ).decode("utf-8")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except:
            return
        return User.query.get(id)

    def to_dict(self, include_email=False):
        # A DB object can't be directly serialize to JSON, just only Python objects could be
        # serialized and written as db like objects.
        data = {
            "id": self.id,
            "username": self.username,
            "last_seen": self.last_seen.isoformat() + "Z",
            # "cell_number": self.cell_number,
            # "club_site_login": self.club_site_login,
            # "club_site_password": self.club_site_password,
            "club_name": self.club_name,
            "club_no": self.club_no,
            "classes": self.classes,
            "_links": {
                "self": url_for("api.get_user", id=self.id),
                "trainings": url_for("api.get_user_trainings", id=self.id),
                "avatar": self.avatar(128),
            },
        }
        if include_email:
            data["email"] = self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in [
            "username",
            "email",
            "cell_number",
            "club_site_login",
            "club_name",
            "club_no",
            "classes",
        ]:
            if field in data:
                setattr(self, field, data[field])
        if new_user and "password" in data:
            self.set_password(data["password"])
        if new_user and "club_site_password" in data:
            self.encrypt_site_password(data["club_site_password"])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode("utf-8")
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
    __tablename__ = "train"

    id = db.Column(db.Integer, primary_key=True)
    your_training = db.Column(db.String(50))
    training_datetime = db.Column(db.DateTime, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    acceptance = db.Column(db.String(20), default="nie")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"<Training {self.your_training}>"

    def to_dict(self, include_email=False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "your_training": self.your_training,
            "training_datetime": self.training_datetime,
            "acceptance": self.acceptance,
            "_links": {"self": url_for("api.get_user_trainings", id=self.id)},
        }
        return data

    def from_dict(self, data):
        for field in [
            "user_id",
            "your_training",
            "training_datetime",
            "training_acceptance",
        ]:
            if field in data:
                setattr(self, field, data[field])
