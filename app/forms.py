from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Length
from app.models import User
from wtforms import TextAreaField

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    cell_number = StringField('Cell number', validators=[DataRequired(), Regexp('^48[0-9]{9}$')])
    club_site_login = StringField('Club site login', validators=[DataRequired(), Email()])
    club_site_password = PasswordField('Club site password', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', 
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email adress.')

    def validate_club_site_login(self, club_site_login):
        user = User.query.filter_by(club_site_login=club_site_login.data).first()
        if user is not None:
            raise ValidationError('Please use a different club site login.')

    def validate_cell_number(self, cell_number):
        user = User.query.filter_by(cell_number=cell_number.data).first()
        if user is not None:
            raise ValidationError('Please use a different cell number.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    yoga = BooleanField('Yoga')
    bodypump = BooleanField('Bodypump')
    calistenics = BooleanField('Calistenics')
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class ActivityForm(FlaskForm):
    activity = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')