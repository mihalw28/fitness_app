# from flask import request
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Regexp, ValidationError

from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    classes = SelectField(
        "My classes",
        choices=[
            ("Kalistenika", "Kalistenika"),
            ("Pilates", "Pilates"),
            ("ZUMBA", "ZUMBA"),
            ("ABT", "ABT"),
            ("Yoga", "YOGA"),
            ("Bodypump", "Bodypump"),
            ("Bodybalance", "Bodybalance"),
            ("Stretching", "Stretching"),
            ("Trening Funkcjonalny", "Trening Funkcjonalny"),
            ("Saf Aqua", "Saf Aqua"),
            ("RUNMAGEDDON", "RUNMAGEDDON"),
            ("Cycling", "Cycling"),
        ],
        validators=[DataRequired()],
    )
    club_name = SelectField(
        "My gym",
        choices=[
            ("22", "Posnania"),
            ("24", "Bałtyk"),
            ("4", "GreenPoint"),
            ("1", "Kinepolis"),
        ],
        validators=[DataRequired()],
    )
    cell_number = StringField(
        "Numer telefonu komórkowego", validators=[DataRequired(), Regexp("^[0-9]{9}$")]
    )
    submit = SubmitField("Submit")

    def __init__(self, original_username, original_cell_number, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_cell_number = original_cell_number

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Proszę użyć innej nazwy uzytkownika.")

    def validate_cell_number(self, cell_number):
        if cell_number.data != self.original_cell_number:
            cell_number = User.query.filter_by(
                cell_number=self.cell_number.data
            ).first()
            if cell_number is not None:
                raise ValidationError("Ten numer jest już w bazie. Proszę wybrać inny.")
