from main.setup import app, db
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)


from main import routes