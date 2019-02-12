from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Length
from app.models import User

class LoginForm(FlaskForm):
    """User LogIn."""
    username = StringField('Nazwa użytkownika', validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    remember_me = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj się')


class RegistrationForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    cell_number = StringField('Numer telefonu komórkowego', validators=[DataRequired(), Regexp('^[0-9]{9}$')])
    club_site_login = StringField('Email wykorzystywany do logowania na stronie siłowni', validators=[DataRequired(), Email()])
    club_site_password = PasswordField('Hasło do logowania na stronie siłowni', validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    password2 = PasswordField('Powtórz hasło', 
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Rejestracja')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Wybrana nazwa użytkownika jest już zajęta.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Podany adres email jest już zajęty')

    def validate_club_site_login(self, club_site_login):
        user = User.query.filter_by(club_site_login=club_site_login.data).first()
        if user is not None:
            raise ValidationError('Wybrana nazwa juz istnieje.')

    def validate_cell_number(self, cell_number):
        user = User.query.filter_by(cell_number=cell_number.data).first()
        if user is not None:
            raise ValidationError('Prosze wpisać inny numer telefonu.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Wyślij nowe hasło')


class ResetPasswordForm(FlaskForm):
    password =PasswordField('Nowe hasło', validators=[DataRequired()])
    password2 = PasswordField('Powtórz hasło', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Zapisz')
