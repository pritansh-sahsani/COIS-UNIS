from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectMultipleField, TextAreaField, SelectField
from wtforms.fields import DateField
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import EqualTo, Email, Length, ValidationError, DataRequired
from flask_wtf.file import FileAllowed, FileField
import re

from main.models import User, Uni

min_max_error_message = """{field} Length Must Be Between {min} and {max} characters!"""

def v_dp_score(dp_score):
    if dp_score.data != "":
        if dp_score.data.isdigit():
            if not (int(dp_score.data) > 0 and int(dp_score.data) <= 45):
                raise ValidationError('Please enver a valid DP score (between 0 and 45).')
        else:
            raise ValidationError('Please enter a valid DP score.')
        
def v_dp_pred(dp_predicted):
    if dp_predicted.data != "":    
        if dp_predicted.data.isdigit():
            if not (int(dp_predicted.data) > 0 and int(dp_predicted.data) <= 45):
                raise ValidationError('Please enver a valid DP predicted (between 0 and 45).')
        else:
            raise ValidationError('Please enter a valid DP predicted.')

def v_myp_score(myp_score):
    if myp_score.data != "":
        if myp_score.data.isdigit():
            if not (int(myp_score.data) > 0 and int(myp_score.data) <= 56 ):
                raise ValidationError('Please enver a valid MYP-5 score (between 0 and 56).')
        else:
            raise ValidationError('Please enter a valid MYP-5 score.')

class AddUniversityForm(FlaskForm):
    name = StringField('University Name', validators=[Length(min=1, max=100, message=min_max_error_message.format(field='University Name', min='%(min)d', max='%(max)d'))])
    logo = FileField('logo', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Only .jpg, .png and .jpeg file formats are supported.')])
    banner = FileField('banner', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Only .jpg, .png and .jpeg file formats are supported.')])
    website = StringField('University Official Website', validators=[Length(max=1000, message=min_max_error_message.format(field='Website', min=0, max='%(max)d'))])
    ib_cutoff = StringField('Cut off/required grade for IBDP')
    min_gpa = StringField('Minimum GPA', validators=[Length(max=10, message=min_max_error_message.format(field='Minimum GPA', min=0, max='%(max)d'))])
    requirements = TextAreaField('Requirements for admission', validators=[Length(max=2000, message=min_max_error_message.format(field='Requirements', min=0, max='%(max)d'))])
    scholarships = TextAreaField('Scholarships offered', validators=[Length(max=1000, message=min_max_error_message.format(field='Scholarship', min=0, max='%(max)d'))])
    acceptance_rate = StringField('Acceptance Rate', validators=[Length(max=10, message=min_max_error_message.format(field='Acceptance rate', min=0, max='%(max)d'))])
    avg_cost = StringField('Average Cost', validators=[Length(max=10, message=min_max_error_message.format(field='Average cost', min=0, max='%(max)d'))])
    email = StringField('Contact Email', validators=[Length(max=100, message=min_max_error_message.format(field='Contact Email', min=0, max='%(max)d'))])
    courses = SelectMultipleField('Courses Offered', choices=[])
    location = StringField('Location')
    
    save_draft = SubmitField('Save As Draft')
    submit = SubmitField('Add University')


    def __init__(self, formdata=None, **kwargs):
        super(AddUniversityForm, self).__init__(formdata=formdata, **kwargs)
        self.courses.choices = kwargs['courses']
    
class UploadCSVForm(FlaskForm):
    csv_file = FileField('CSV File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ])
    images_zip = FileField('Images ZIP', validators=[
        FileRequired(),
        FileAllowed(['zip'], 'ZIP files only!')
    ])
    submit = SubmitField('Upload Files')


class AdmissionForm(FlaskForm):
    grade_sought = StringField('Grade in which admission is sought')
    academic_year = StringField('Academic Year')
    student_first_name = StringField('Student First Name')
    student_middle_name = StringField('Student Middle Name')
    student_last_name = StringField('Student Last Name')
    dob = DateField('Date of Birth (dd/mm/yyyy)', format='%Y-%m-%d', validators=[DataRequired()])
    place_of_birth = StringField('Place of Birth')
    nationality = StringField('Nationality')
    religion = StringField('Religion')
    father_name = StringField("Father's Name")
    father_nationality = StringField("Father's Nationality")
    father_profession = StringField("Father's Profession")
    father_designation = StringField("Father's Designation")
    father_organisation = StringField("Father's Organisation")
    father_mobile = StringField("Father's Mobile")
    father_email = StringField("Father's Email")
    mother_name = StringField("Mother's Name")
    mother_nationality = StringField("Mother's Nationality")
    mother_profession = StringField("Mother's Profession")
    mother_designation = StringField("Mother's Designation")
    mother_organisation = StringField("Mother's Organisation")
    mother_mobile = StringField("Mother's Mobile")
    mother_email = StringField("Mother's Email")
    home_address = TextAreaField('Home Address')
    home_phone = StringField('Home Phone Number')
    school_last_attended = StringField('School Last Attended')
    board = StringField('Board Followed by Last School')
    class_studying = StringField('Class Currently Studying In')
    extra_curricular_interests = TextAreaField('Extra-curricular Interests')
    allergies = TextAreaField('Allergies')
    blood_group = StringField('Blood Group')
    submit = SubmitField('Submit')

    def __init__(self, formdata=None, **kwargs):
        super(AdmissionForm, self).__init__(formdata=formdata, **kwargs)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=1, max=120, message=min_max_error_message.format(field='Username', min='%(min)d', max='%(max)d'))])
    password = PasswordField('Password', validators=[Length(min=1, max=60, message=min_max_error_message.format(field='Password', min='%(min)d', max='%(max)d'))])
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
    pfp = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Only .jpg, .png and .jpeg file formats are supported.')])
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
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    phone_number = StringField("Phone Number", validators=[Length(min=1, max=13, message=min_max_error_message.format(field='Phone Number', min='%(min)d', max='%(max)d'))])
    pfp = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Only .jpg, .png and .jpeg file formats are supported.')])
    submit = SubmitField('Confirm Changes')

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
    phone_number = StringField("Phone Number", validators=[Length(min=1, max=13, message=min_max_error_message.format(field='Phone Number', min='%(min)d', max='%(max)d'))])
    pfp = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Only .jpg, .png and .jpeg file formats are supported.')])
    
    graduation_year = StringField("Graduatation Year", validators=[Length(min=4, max=4, message="Please enter a valid graduation year.")])
    myp_score = StringField('MYP-5 Score (out of 56)')
    dp_predicted = StringField('DP predicted score (out of 45)')
    dp_score = StringField('DP score (out of 45)')
    has_diploma = BooleanField('Diploma certificate')
    portfolio = StringField('Link to portfolio (Optional)')
    
    submit = SubmitField('Sign Up')

    def validate_dp_predicted(self, dp_predicted):
        v_dp_pred(dp_predicted)
            
    def validate_dp_score(self, dp_score):
        v_dp_score(dp_score)

    def validate_myp_score(self, myp_score):
        v_myp_score(myp_score)

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
        
    def validate_graduation_year(self, graduation_year):
        if graduation_year.data !="":
            if graduation_year.data.isdigit():
                if int(graduation_year.data) < 2010 or int(graduation_year.data) > 2037:
                    raise ValidationError('Please enter a valid graduation year.')
            else:
                raise ValidationError('Please enter a valid graduation year.')
    
    def __init__(self, formdata=None, **kwargs):
        super(StudentRegistrationForm, self).__init__(formdata=formdata, **kwargs)


class EditStudentForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=1, max=50, message=min_max_error_message.format(field='Username', min='%(min)d', max='%(max)d'))])
    fullname = StringField('Full Name', validators=[Length(min=1, max=50, message=min_max_error_message.format(field='Full name', min='%(min)d', max='%(max)d'))])
    email = StringField('Email', validators=[Length(min=1, max=120, message=min_max_error_message.format(field='Email', min='%(min)d', max='%(max)d')), Email()])
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    phone_number = StringField("Phone Number", validators=[Length(min=1, max=13, message=min_max_error_message.format(field='Phone Number', min='%(min)d', max='%(max)d'))])
    pfp = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Only .jpg, .png and .jpeg file formats are supported.')])
    
    graduation_year = StringField("Graduatation Year", validators=[Length(min=4, max=4, message="Please enter a valid graduation year.")])
    myp_score = StringField('MYP-5 Score (out of 56)')
    dp_predicted = StringField('DP predicted score (out of 45)')
    dp_score = StringField('DP score (out of 45)')
    has_diploma = BooleanField('Diploma certificate')
    portfolio = StringField('Link to portfolio (Optional)')
    
    submit = SubmitField('Confirm Changes')

    def validate_dp_predicted(self, dp_predicted):
        v_dp_pred(dp_predicted)
            
    def validate_dp_score(self, dp_score):
        v_dp_score(dp_score)

    def validate_myp_score(self, myp_score):
        v_myp_score(myp_score)

    def validate_email(self, email):
        if not email.data.endswith("@cois.edu.in"):
            raise ValidationError('Please register with your COIS email id.')

    def validate_graduation_year(self, graduation_year):
        if graduation_year.data !="":
            if graduation_year.data.isdigit():
                if int(graduation_year.data) < 2010 or int(graduation_year.data) > 2037:
                    raise ValidationError('Please enter a valid graduation year.')
            else:
                raise ValidationError('Please enter a valid graduation year.')
    
    def __init__(self, formdata=None, **kwargs):
        super(EditStudentForm, self).__init__(formdata=formdata, **kwargs)


class ApplicationForm(FlaskForm):
    uni = SelectField('University', choices=[])
    course = SelectField('Course', choices=[])
    minors = SelectMultipleField('Minors, if any', choices=[])
    status = SelectField('Application status (if recieved)', choices=['considering', 'applied', 'waitlist', 'accepted', 'rejected'])
    is_early = BooleanField('Early Application')
    scholarship = StringField('Scholarship if recieved any')
    selected_uni = BooleanField('Is this the university you have taken admission in?')
    other_details = TextAreaField('Other details that you feel would be useful for other students to know.')
    submit = SubmitField('Submit')

    def __init__(self, formdata=None, **kwargs):
        super(ApplicationForm, self).__init__(formdata=formdata, **kwargs)
        self.course.choices = kwargs['courses']
        self.minors.choices = kwargs['minors']
        self.uni.choices = kwargs['unis']


class FilterForm(FlaskForm):
    requirements = StringField('Requirements for admission')
    scholarships = StringField('Scholarships')
    courses = SelectField('Courses', choices=[])
    location = SelectField('Location', choices=[])
    min_ib_cutoff = StringField('Minimum Cut off for IBDP')
    max_ib_cutoff = StringField('Maximum Cut off for IBDP')
    min_acceptance_rate = StringField('Minimum Acceptance Rate')
    max_acceptance_rate = StringField('Maximum Acceptance Rate')
    min_avg_cost = StringField('Minimum Average Cost')
    max_avg_cost = StringField('Maximum Average Cost')
    min_gpa = StringField('Minimum GPA')
    max_gpa = StringField('Maximum GPA')
    
    submit = SubmitField('Apply Filter')
    clear = SubmitField('Clear Filters')
    coisstudents = BooleanField('COIS students')

    def __init__(self, formdata=None, **kwargs):
        super(FilterForm, self).__init__(formdata=formdata, **kwargs)
        self.courses.choices = kwargs['courses']
        self.location.choices = kwargs['locations']
        
class FilterStudentsForm(FlaskForm):
    graduation_year = StringField("Graduatation Year", validators=[Length(max=4, message="Please enter a valid graduation year.")])
    myp_score_min = StringField('Minimum MYP-5 Score (out of 56)')
    myp_score_max = StringField('Maximum MYP-5 Score (out of 56)')
    dp_predicted_min = StringField('Minimum DP predicted')
    dp_predicted_max = StringField('Maximum DP predicted')
    dp_score_min = StringField('Minimum DP score')
    dp_score_max = StringField('Maximum DP score')
    has_diploma = BooleanField('Diploma Certificate')

    uni = SelectField('University', choices=[])
    course = SelectField('Course', choices=[])
    location = SelectField('Location')
    status = SelectField('Application status', choices=['Application Status', 'waitlist', 'accepted', 'rejected'])
    is_early = BooleanField('Early Application')
    selected_uni = BooleanField('Took admission')

    submit = SubmitField('Apply Filter')
    clear = SubmitField('Clear Filters')

    def validate_graduation_year(self, graduation_year):
        if graduation_year.data !="" and graduation_year.data is not None:
            if not graduation_year.data.isdigit():
                raise ValidationError('Please enter a valid graduation year.')
    
    def validate_myp_score_min(self, myp_score_min):v_myp_score(myp_score_min)
    def validate_myp_score_max(self, myp_score_max):v_myp_score(myp_score_max)
    def validate_dp_score_min(self, dp_score_min):v_dp_score(dp_score_min)
    def validate_dp_score_max(self, dp_score_max):v_dp_score(dp_score_max)
    def validate_dp_predicted_min(self, dp_predicted_min):v_dp_pred(dp_predicted_min)
    def validate_dp_predicted_max(self, dp_predicted_max):v_dp_pred(dp_predicted_max)
    
    def __init__(self, formdata=None, **kwargs):
        super(FilterStudentsForm, self).__init__(formdata=formdata, **kwargs)
        self.course.choices = kwargs['courses']
        self.uni.choices = kwargs['unis']
        self.location.choices = kwargs['locations']