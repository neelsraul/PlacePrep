import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'neelsraul'
    SQLALCHEMY_DATABASE_URI = os.environ.get('postgresql://postgres:neelsraul@localhost:5432/UserData') or \
        'postgresql://postgres:neelsraul@localhost:5432/UserData'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads/'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limit file size to 16MB
