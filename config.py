import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'neelsraul')

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:neelsraul@localhost:5432/UserData')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File Uploads
    UPLOAD_FOLDER = 'uploads/'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limit file size to 16MB

    # Google Gemini API Key (Use environment variable for security)
    GOOGLE_GEMINI_API_KEY = os.environ.get('GOOGLE_GEMINI_API_KEY', 'AIzaSyBdiTBiBBTNIacb1ZJVpbbicjJ-uLSSzek')
