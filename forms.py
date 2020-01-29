from flask_wtf import Form 
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, DateField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                    Length, EqualTo)
from models import User

def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError("User with that name already exists")


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError("User with that email already exists")

class RegisterForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters,"
                " numbers, and underscores only.")
            ),
            name_exists
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8),
            EqualTo('password2', message="Passwords must match")
        ]
    )
    password2 = PasswordField(
        'Password2',
        validators=[
            DataRequired()
        ]
    )


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class AddEntryForm(Form):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('What is up?', validators=[DataRequired()])
    time_spent = StringField('Time spent on studying', validators=[DataRequired()])
    resources = TextAreaField('Resources to remember', validators=[DataRequired()])
    date = DateField('Date format: year-month-day', validators=[DataRequired()], format='%Y-%m-%d')
