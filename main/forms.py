from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectMultipleField, TextAreaField
from wtforms.validators import EqualTo, Email, Length, ValidationError, DataRequired
from flask_wtf.file import FileAllowed, FileField

from main.models import User

min_max_error_message = """{field} Length Must Be Between {min} and {max} characters!"""

class AddUniversityForm(FlaskForm):
    name = StringField('University Name', validators=[Length(min=1, max=100, message=min_max_error_message.format(field='University Name', min='%(min)d', max='%(max)d'))])
    logo = FileField('logo', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Only .jpg, .png and .jpeg file formats are supported.')])
    website = StringField('University Official Website', validators=[Length(max=1000, message=min_max_error_message.format(field='Website', min=0, max='%(max)d'))])
    ib_cutoff = StringField('Cut off/required grade for IBDP')
    requirements = TextAreaField('Requirements for admission')
    scholarships = TextAreaField('Scholarships offered')
    courses = SelectMultipleField('Courses Offered', choices=[])
    location = SelectMultipleField('Location', choices=[])
    
    save_draft = SubmitField('Save As Draft')
    submit = SubmitField('Add University')

    def __init__(self, formdata=None, **kwargs):
        super(AddUniversityForm, self).__init__(formdata=formdata, **kwargs)
        self.courses.choices = kwargs['courses']
        self.location.choices = kwargs['locations']
    

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


class FilterForm(FlaskForm):
    ib_cutoff = StringField('Cut off/required grade for IBDP')
    requirements = StringField('Requirements for admission')
    scholarships = StringField('Scholarships')
    courses = SelectMultipleField('Courses', choices=[])
    location = SelectMultipleField('Location', choices=[])
    submit = SubmitField('Apply Filter')
    clear = SubmitField('Clear Filters')

    def __init__(self, formdata=None, **kwargs):
        super(FilterForm, self).__init__(formdata=formdata, **kwargs)
        self.courses.choices = kwargs['courses']
        self.location.choices = kwargs['locations']


class AddCourseForm(FlaskForm):
    name = StringField('Course', validators=[DataRequired()])
    submit = SubmitField('Add Course')


class AddLocationForm(FlaskForm):
    name = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Add Location')