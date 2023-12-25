
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
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    added_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

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
        return f"User('{self.username}', '{self.email}')"


locations_table = db.Table(
    'location_association',
    db.Column('uni_id', db.ForeignKey('uni.id'), primary_key=True),
    db.Column('location_id', db.ForeignKey('location.id'), primary_key=True),
)

courses_table = db.Table(
    'course_association',
    db.Column('uni_id', db.ForeignKey('uni.id'), primary_key=True),
    db.Column('course_id', db.ForeignKey('course.id'), primary_key=True),
)

class Uni(db.Model):
    __searchable__ = ['name']
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

class Location(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    unis = relationship('Uni', secondary=locations_table, back_populates='locations')


class Course(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unis = relationship('Uni', secondary=courses_table, back_populates='courses')
    

with app.app_context():
    db.create_all()
    db.session.commit()