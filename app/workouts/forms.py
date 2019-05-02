from flask_wtf import FlaskForm
from wtforms import HiddenField, SubmitField


class SignUpForTrainingForm(FlaskForm):
    training_activity = HiddenField()
    submit = SubmitField("Sign Up")


class CancelTrainingForm(FlaskForm):
    submit = SubmitField("Anuluj rezerwację")
