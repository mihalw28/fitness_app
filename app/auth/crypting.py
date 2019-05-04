import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import current_app


def decrypt_gym_password(user):
    """Gets encrypted user's gym site password, decrypts it and returns string.

    Parameters:
        user : User from data base.

    Returns:
        plain_text_password (str) : User's gym password.

    """
    b_club_site_password = (user.club_site_password).encode("utf-8")
    hash_key = current_app.config["HASH_KEY"]
    b_hash_key = hash_key.encode("utf-8")
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(b_hash_key))
    cipher_suite = Fernet(key)
    decrypted_password = cipher_suite.decrypt(b_club_site_password)
    plain_text_password = bytes(decrypted_password).decode("utf-8")
    return plain_text_password
