from cryptography.fernet import Fernet
from flask import current_app

def decrypt_gym_password(user):
    """Gets encrypted user's gym site password, decrypts it and returns string.
    Parameters:
        user : User from data base.
    Returns:
        plain_text_password (str) : User's gym password.
    """
    # Change user gym password from plain string to binary
    b_gym_password = (user.club_site_password).encode("utf-8")
    f = Fernet(current_app.config['KEY'])
    b_decrypted_password = f.decrypt(b_gym_password)
    plain_text_password = bytes(b_decrypted_password).decode("utf-8")
    return plain_text_password
