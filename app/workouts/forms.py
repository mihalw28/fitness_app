# from flask import request
from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField


class SignUpForTrainingForm(FlaskForm):
    training_activity = HiddenField()
    submit = SubmitField("Sign Up")


class CancelTrainingForm(FlaskForm):
    submit = SubmitField("Anuluj rezerwację")
