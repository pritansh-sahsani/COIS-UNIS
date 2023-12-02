import os

class Config:
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'COISUNIS.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    MSEARCH_INDEX_NAME = 'msearch'
    MSEARCH_PRIMARY_KEY = 'id'
    MSEARCH_ENABLE = True