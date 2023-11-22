
from main.setup import app, db, login_manager
from flask_login import UserMixin
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __searchable__ = ['username', 'email']

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

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

class Messages(db.Model):
    __searchable__ = ['message', 'name']
    id= db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(4000), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    read = db.Column(db.Boolean, nullable = False, default=False)
    replied = db.Column(db.Boolean, nullable = False, default=False)
    
class MessageReply(db.Model):
    id= db.Column(db.Integer, nullable=False, primary_key=True)
    message_id = db.Column(db.Integer, nullable=False)
    reply = db.Column(db.String(4000), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)

with app.app_context():
    db.create_all()
    db.session.commit()