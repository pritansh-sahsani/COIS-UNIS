from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectMultipleField, TextAreaField
from wtforms.validators import EqualTo, Email, Length, ValidationError
from flask_wtf.file import FileAllowed, FileField
import re

from main.models import User, Uni

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

    def validate_name(self, name):
        uni = Uni.query.filter_by(name=name.data).first()
        if uni:
            raise ValidationError('A university with that name has already been added.')

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


class AdminRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=1, max=50, message=min_max_error_message.format(field='Username', min='%(min)d', max='%(max)d'))])
    fullname = StringField('Full Name', validators=[Length(min=1, max=50, message=min_max_error_message.format(field='Full name', min='%(min)d', max='%(max)d'))])
    email = StringField('Email', validators=[Length(min=1, max=120, message=min_max_error_message.format(field='Email', min='%(min)d', max='%(max)d')), Email()])
    password = PasswordField('Password', validators=[Length(min=1, max=60, message=min_max_error_message.format(field='Password', min='%(min)d', max='%(max)d'))])
    confirm_password = PasswordField('Confirm Password', validators=[Length(min=1, max=60, message=min_max_error_message.format(field='Confirm Password', min='%(min)d', max='%(max)d')), EqualTo('password')])
    phone_number = StringField("Phone Number", validators=[Length(min=1, max=13, message=min_max_error_message.format(field='Password', min='%(min)d', max='%(max)d'))])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different username.')
        pattern = r'[!@#$%^&*()_+={}\[\]:;"\'|,.<>?\\\/~`\s]'
        if re.search(pattern, username.data):
            return ValidationError('User name should not contain spaces or special characters.')
    
    def validate_phone_number(self, phone_number):
        user = User.query.filter_by(phone_number=phone_number.data).first()
        if user:
            raise ValidationError('An account is already registered with this phone number.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please register using a different email address.')
        if not email.data.endswith("@cois.edu.in"):
            raise ValidationError('Please register with your COIS email id.')

    def __init__(self, formdata=None, **kwargs):
        super(AdminRegistrationForm, self).__init__(formdata=formdata, **kwargs)


class EditAdminForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=1, max=50, message=min_max_error_message.format(field='Username', min='%(min)d', max='%(max)d'))])
    fullname = StringField('Full Name', validators=[Length(min=1, max=50, message=min_max_error_message.format(field='Full name', min='%(min)d', max='%(max)d'))])
    email = StringField('Email', validators=[Length(min=1, max=120, message=min_max_error_message.format(field='Email', min='%(min)d', max='%(max)d')), Email()])
    password = PasswordField('Password', validators=[Length(min=1, max=60, message=min_max_error_message.format(field='Password', min='%(min)d', max='%(max)d'))])
    confirm_password = PasswordField('Confirm Password', validators=[Length(min=1, max=60, message=min_max_error_message.format(field='Confirm Password', min='%(min)d', max='%(max)d')), EqualTo('password')])
    phone_number = StringField("Phone Number", validators=[Length(min=1, max=13, message=min_max_error_message.format(field='Password', min='%(min)d', max='%(max)d'))])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        pattern = r'[!@#$%^&*()_+={}\[\]:;"\'|,.<>?\\\/~`\s]'
        if re.search(pattern, username.data):
            return ValidationError('User name should not contain spaces or special characters.')
        
    def validate_email(self, email):
        if not email.data.endswith("@cois.edu.in"):
            raise ValidationError('Please register with your COIS email id.')
        
    def __init__(self, formdata=None, **kwargs):
        super(EditAdminForm, self).__init__(formdata=formdata, **kwargs)


class StudentRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=1, max=50, message=min_max_error_message.format(field='Username', min='%(min)d', max='%(max)d'))])
    fullname = StringField('Full Name', validators=[Length(min=1, max=50, message=min_max_error_message.format(field='Full name', min='%(min)d', max='%(max)d'))])
    email = StringField('Email', validators=[Length(min=1, max=120, message=min_max_error_message.format(field='Email', min='%(min)d', max='%(max)d')), Email()])
    password = PasswordField('Password', validators=[Length(min=1, max=60, message=min_max_error_message.format(field='Password', min='%(min)d', max='%(max)d'))])
    confirm_password = PasswordField('Confirm Password', validators=[Length(min=1, max=60, message=min_max_error_message.format(field='Confirm Password', min='%(min)d', max='%(max)d')), EqualTo('password')])
    phone_number = StringField("Phone Number", validators=[Length(min=1, max=13, message=min_max_error_message.format(field='Password', min='%(min)d', max='%(max)d'))])

    myp_score = StringField('MYP-5 Score (out of 56)')
    dp_predicted = StringField('DP predicted score (out of 45)')
    dp_score = StringField('DP score (out of 45)')
    has_diploma = BooleanField('Diploma certificate')
    portfolio = StringField('Link to portfolio (Optional)')
    
    submit = SubmitField('Sign Up')

    def validate_dp_predicted(self, dp_predicted):
        if dp_predicted.data != "":    
            if dp_predicted.data.isdigit():
                if not (int(dp_predicted.data) > 0 and int(dp_predicted.data) <= 45):
                    raise ValidationError('Please enver a valid DP predicted (between 0 and 45).')
            else:
                raise ValidationError('Please enter a valid DP predicted.')
            
    def validate_dp_score(self, dp_score):
        if dp_score.data != "":
            if dp_score.data.isdigit():
                if not (int(dp_score.data) > 0 and int(dp_score.data) <= 45):
                    raise ValidationError('Please enver a valid DP score (between 0 and 45).')
            else:
                raise ValidationError('Please enter a valid DP score.')

    def validate_myp_score(self, myp_score):
        if myp_score.data != "":
            if myp_score.data.isdigit():
                if not (int(myp_score.data) > 0 and int(myp_score.data) <= 56 ):
                    raise ValidationError('Please enver a valid MYP-5 score (between 0 and 56).')
            else:
                raise ValidationError('Please enter a valid MYP-5 score.')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different username.')
    
    def validate_phone_number(self, phone_number):
        user = User.query.filter_by(phone_number=phone_number.data).first()
        if user:
            raise ValidationError('An account is already registered with this phone number.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please register using a different email address.')
        if not email.data.endswith("@cois.edu.in"):
            raise ValidationError('Please register with your COIS email id.')

    def __init__(self, formdata=None, **kwargs):
        super(StudentRegistrationForm, self).__init__(formdata=formdata, **kwargs)


class EditStudentForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=1, max=50, message=min_max_error_message.format(field='Username', min='%(min)d', max='%(max)d'))])
    fullname = StringField('Full Name', validators=[Length(min=1, max=50, message=min_max_error_message.format(field='Full name', min='%(min)d', max='%(max)d'))])
    email = StringField('Email', validators=[Length(min=1, max=120, message=min_max_error_message.format(field='Email', min='%(min)d', max='%(max)d')), Email()])
    password = PasswordField('Password', validators=[Length(min=1, max=60, message=min_max_error_message.format(field='Password', min='%(min)d', max='%(max)d'))])
    confirm_password = PasswordField('Confirm Password', validators=[Length(min=1, max=60, message=min_max_error_message.format(field='Confirm Password', min='%(min)d', max='%(max)d')), EqualTo('password')])
    phone_number = StringField("Phone Number", validators=[Length(min=1, max=13, message=min_max_error_message.format(field='Password', min='%(min)d', max='%(max)d'))])

    myp_score = StringField('MYP-5 Score (out of 56)')
    dp_predicted = StringField('DP predicted score (out of 45)')
    dp_score = StringField('DP score (out of 45)')
    has_diploma = BooleanField('Diploma certificate')
    portfolio = StringField('Link to portfolio (Optional)')
    
    submit = SubmitField('Confirm Changes')

    def validate_dp_predicted(self, dp_predicted):
        if dp_predicted.data != "":    
            if dp_predicted.data.isdigit():
                if not (int(dp_predicted.data) > 0 and int(dp_predicted.data) <= 45):
                    raise ValidationError('Please enver a valid DP predicted (between 0 and 45).')
            else:
                raise ValidationError('Please enter a valid DP predicted.')
            
    def validate_dp_score(self, dp_score):
        if dp_score.data != "":
            if dp_score.data.isdigit():
                if not (int(dp_score.data) > 0 and int(dp_score.data) <= 45):
                    raise ValidationError('Please enver a valid DP score (between 0 and 45).')
            else:
                raise ValidationError('Please enter a valid DP score.')

    def validate_myp_score(self, myp_score):
        if myp_score.data != "":
            if myp_score.data.isdigit():
                if not (int(myp_score.data) > 0 and int(myp_score.data) <= 56 ):
                    raise ValidationError('Please enver a valid MYP-5 score (between 0 and 56).')
            else:
                raise ValidationError('Please enter a valid MYP-5 score.')

    def validate_email(self, email):
        if not email.data.endswith("@cois.edu.in"):
            raise ValidationError('Please register with your COIS email id.')

    def __init__(self, formdata=None, **kwargs):
        super(EditStudentForm, self).__init__(formdata=formdata, **kwargs)


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