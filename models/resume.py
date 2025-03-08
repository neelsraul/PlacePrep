from datetime import datetime
from extensions import db

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    education = db.Column(db.Text)        # Field for storing education details from parsed data
    skills = db.Column(db.Text)           # Field for storing skills from parsed data
    experience = db.Column(db.Text)       # Field for storing experience from parsed data
    recommendations = db.Column(db.Text)  # Field for storing job recommendations
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Optional: Initialize with all attributes to ensure consistency
    def __init__(self, filename, user_id, education=None, skills=None, experience=None, recommendations=None):
        self.filename = filename
        self.upload_date = datetime.utcnow()
        self.education = education
        self.skills = skills
        self.experience = experience
        self.recommendations = recommendations
        self.user_id = user_id
