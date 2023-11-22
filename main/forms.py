from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import EqualTo, Email, Length, ValidationError

from main.models import User

min_max_error_message = """{field} Length Must Be Between {min} and {max} characters!"""

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=1, max=120, message=min_max_error_message.format(field='Username', min='%(min)d', max='%(max)d'))])
    password = PasswordField('Password', validators=[Length(min=1, max=60, message=min_max_error_message.format(field='Password', min='%(min)d', max='%(max)d'))])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
    def __init__(self, formdata=None, **kwargs):
        super(LoginForm, self).__init__(formdata=formdata, **kwargs)


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=1, max=30, message=min_max_error_message.format(field='Username', min='%(min)d', max='%(max)d'))])
    email = StringField('Email', validators=[Length(min=1, max=120, message=min_max_error_message.format(field='Email', min='%(min)d', max='%(max)d')), Email()])
    password = PasswordField('Password', validators=[Length(min=1, max=60, message=min_max_error_message.format(field='Password', min='%(min)d', max='%(max)d'))])
    confirm_password = PasswordField('Confirm Password', validators=[Length(min=1, max=60, message=min_max_error_message.format(field='Confirm Password', min='%(min)d', max='%(max)d')), EqualTo('password')])
    super_user_key = StringField('Super User Key', validators=[Length(min=1, max=100, message=min_max_error_message.format(field='Super User Key', min='%(min)d', max='%(max)d'))])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError('That username is already taken. Please choose a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('That email is already registered. Please register using a different email address.')

    def __init__(self, formdata=None, **kwargs):
        super(RegistrationForm, self).__init__(formdata=formdata, **kwargs)


class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=1, max=30, message=min_max_error_message.format(field='Username', min='%(min)d', max='%(max)d'))])
    email = StringField('Email', validators=[Length(min=1, max=120, message=min_max_error_message.format(field='Email', min='%(min)d', max='%(max)d')), Email()])
    password = PasswordField('Password', validators=[Length(min=0, max=60, message=min_max_error_message.format(field='Password', min='%(min)d', max='%(max)d'))])
    confirm_password = PasswordField('Confirm Password', validators=[Length(min=0, max=60, message=min_max_error_message.format(field='Confirm Password', min='%(min)d', max='%(max)d')), EqualTo('password')])
    super_user_key = StringField('Super User Key', validators=[Length(min=1, max=100, message=min_max_error_message.format(field='Super User Key', min='%(min)d', max='%(max)d'))])
    submit = SubmitField('Confirm Changes')

    def __init__(self, formdata=None, **kwargs):
        super(EditUserForm, self).__init__(formdata=formdata, **kwargs)

        
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[Length(min=1, max=100, message=min_max_error_message.format(field='Name', min='%(min)d', max='%(max)d'))])
    email = StringField('Email', validators=[Length(min=1, max=120, message=min_max_error_message.format(field='Email', min='%(min)d', max='%(max)d')), Email()])
    message = TextAreaField('Message', validators=[Length(min=1, max=4000, message=min_max_error_message.format(field='Message', min='%(min)d', max='%(max)d'))])
    submit = SubmitField('Submit')
    
    def __init__(self, formdata=None, **kwargs):
        super(ContactForm, self).__init__(formdata=formdata, **kwargs)


class MessageReplyForm(FlaskForm):
    reply = TextAreaField('reply', validators=[Length(min=1, max=10000, message=min_max_error_message.format(field='Reply', min='%(min)d', max='%(max)d'))])
    submit = SubmitField('Reply')
    
    def __init__(self, formdata=None, **kwargs):
        super(MessageReplyForm, self).__init__(formdata=formdata, **kwargs)
