from app.models import Users

from flask import request

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


class NewPost(FlaskForm):
    title = StringField('Title', validators=[DataRequired(),
                        Length(max=64)])
    headline = StringField('Headline', validators=[DataRequired(),
                           Length(max=64)])
    body = TextAreaField('Body', validators=[DataRequired()])

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)

class LoginForm(FlaskForm):
    email = EmailField('Email Address', [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = EmailField('Email Address', [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_repeat = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def validate_email(self, email):
        """
        Check if user email exists.
        """
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email is already registered!')