from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, \
    HiddenField
from wtforms.validators import ValidationError, DataRequired, Length, InputRequired
from app.models import User

class SignUpForTrainingForm(FlaskForm):
    training_activity = HiddenField()
    #user_club_number = HiddenField()
    #user_club_login = HiddenField()
    #user_club_password = HiddenField()
    submit = SubmitField("Sign Up")