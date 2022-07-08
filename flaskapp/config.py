import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    VIRUS_TOTAL_API_KEY = os.environ.get('VIRUS_TOTAL_API_KEY')

