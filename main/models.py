from main.setup import app, db, login_manager
from flask_login import UserMixin
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from sqlalchemy.orm import relationship

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __searchable__ = ['username', 'email']

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    fullname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    added_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    phone_number = db.Column(db.String(13), nullable=False, unique=True)
    is_student = db.Column(db.Boolean, nullable=False, default=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}')"

class Student_details(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    myp_score = db.Column(db.Integer)
    graduation_year = db.Column(db.Integer)
    dp_predicted = db.Column(db.Integer)
    dp_score = db.Column(db.Integer)
    has_diploma = db.Column(db.Boolean)
    portfolio = db.Column(db.String(100))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('student_details', lazy=True))

    selected_uni_id = db.Column(db.Integer, db.ForeignKey('uni.id'))
    selected_app_id = db.Column(db.Integer)

    def __repr__(self):
        return f"details-{self.user}"

locations_table = db.Table(
    'location_association',
    db.Column('uni_id', db.ForeignKey('uni.id'), primary_key=True),
    db.Column('location_id', db.ForeignKey('location.id'), primary_key=True),
)

courses_table = db.Table(
    'course_association',
    db.Column('uni_id', db.ForeignKey('uni.id')),
    db.Column('course_id', db.ForeignKey('course.id')),
)

class Uni(db.Model):
    __searchable__ = ['name', 'ib_cutoff', 'requirements', 'scholarships']
    id= db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    logo = db.Column(db.String(104))
    added_at= db.Column(db.DateTime, default=datetime.now)
    ib_cutoff= db.Column(db.Integer)
    website = db.Column(db.String(1000))
    scholarships = db.Column(db.String(1000))
    requirements = db.Column(db.String(1000))
    is_draft = db.Column(db.Boolean, nullable=False)

    locations = relationship('Location', secondary=locations_table, back_populates='unis')
    courses = relationship('Course', secondary=courses_table, back_populates='unis')

    def __repr__(self):
        return f"{self.name}"

class Location(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    exact_location = db.Column(db.String(202), nullable=False)
    unis = relationship('Uni', secondary=locations_table, back_populates='locations')

    def __repr__(self):
        return f"<{self.exact_location}>"

minors_table = db.Table(
    'minor_association',
    db.Column('application_id', db.ForeignKey('application.id'), primary_key=True),
    db.Column('course_id', db.ForeignKey('course.id'), primary_key=True),
)

class Course(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unis = relationship('Uni', secondary=courses_table, back_populates='courses')
    minor_applications = relationship('Application', secondary=minors_table, back_populates='minors')
    def __repr__(self):
        return f"{self.name}"


class Application(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    uni_id = db.Column(db.Integer, db.ForeignKey('uni.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student_details.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    minors = relationship('Course', secondary=minors_table, back_populates='minor_applications')
    status = db.Column(db.String(20))  # Multiclass: waitlist, accepted, rejected
    scholarship = db.Column(db.String(300))
    other_details = db.Column(db.String(2500))
    is_early = db.Column(db.Boolean, nullable=False)

    student = db.relationship('Student_details', backref=db.backref('applications', lazy=True))
    uni = db.relationship('Uni', backref=db.backref('applications', lazy=True))
    course = db.relationship('Course', backref=db.backref('applications', lazy=True))
    location = db.relationship('Location', backref=db.backref('applications', lazy=True))

    def __repr__(self):
        return f"{self.id}"


with app.app_context():
    db.create_all()
    db.session.commit()