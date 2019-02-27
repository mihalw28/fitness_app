from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, \
    SelectField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Length, \
    InputRequired
from app.models import User, Train


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    classes = SelectField('My classes', choices=[('Kalistenika', 'Kalistenika'),
                          ('Pilates', 'Pilates'), ('ZUMBA', 'ZUMBA'),
                          ('ABT', 'ABT'), ('Yoga', 'YOGA'), ('Bodypump',
                          'Bodypump'), ('Bodybalance', 'Bodybalance'),
                          ('Stretching', 'Stretching'), ('Trening Funkcjonalny',
                          'Trening Funkcjonalny'), ('Saf Aqua', 'Saf Aqua'),
                          ('RUNMAGEDDON', 'RUNMAGEDDON'), ('Cycling', 'Cycling')],
                          validators=[DataRequired()])
    club_name = SelectField('My gym', choices=[('22', 'Posnania'),
                            ('24', 'Bałtyk'), ('4', 'GreenPoint'),
                            ('1', 'Kinepolis')], validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


# signup form for workout
class SignUpForm(FlaskForm):
    training = SelectField('Your workouts', choices=[('pi', 'Pilates'),
                           ('zu', 'ZUMBA'), ('ab', 'ABT')],
                           validators=[InputRequired()])
    submit2 = SubmitField("Sign Up")
