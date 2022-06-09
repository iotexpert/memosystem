from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from memos.models.User import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',render_kw={})

    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.find(username=username.data)
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',render_kw={})
    email = StringField('Email',render_kw={})
    delegates = StringField('Delegates', validators=[],render_kw={})
    admin = BooleanField('Admin', render_kw={})

    readAll = BooleanField('Read All', render_kw={})

    subscriptions = StringField('Subscriptions',render_kw={})
    pagesize = StringField('Page Size',render_kw={})
    
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_delegates(self,delegates):
        users = User.valid_usernames(delegates.data)
        if users['non_users']:
            raise ValidationError(f'Invalid users {users["invalid_usernames"]} or email addresses specified.')

    def validate_subscriptions(self,subscriptions):
        users = User.valid_usernames(subscriptions.data)
        if users['non_users']:
            raise ValidationError(f'Invalid users {users["invalid_usernames"]} or email addresses specified.')


class RequestResetForm(FlaskForm):
    """
    This function
    """
    email = StringField('Email',render_kw={})
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
