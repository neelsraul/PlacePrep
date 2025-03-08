from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from models.resume import Resume
from app import db
from utils.parse_resume import parse_resume
from utils.recommend import recommend_job_domains

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.upload_date.desc()).all()
    return render_template('dashboard.html', resumes=resumes)

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_resume():
    if request.method == 'POST':
        # Handle file upload
        file = request.files['resume']
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{current_user.id}_{datetime.utcnow().timestamp()}_{file.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Parse resume
            extracted_info = parse_resume(filepath)

            # Get recommendations
            recommendations = recommend_job_domains(extracted_info)

            # Save to database
            resume = Resume(
                filename=filename,
                upload_date=datetime.utcnow(),
                education=';'.join(extracted_info.get('education', [])),
                skills=';'.join(extracted_info.get('skills', [])),
                experience=';'.join(extracted_info.get('experience', [])),
                recommendations=';'.join(recommendations),
                user_id=current_user.id
            )
            db.session.add(resume)
            db.session.commit()

            # Delete the uploaded file
            os.remove(filepath)

            flash('Resume uploaded and processed successfully')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid file type')
            return redirect(url_for('main.upload_resume'))
    return render_template('upload.html')

@main.route('/resume/<int:resume_id>')
@login_required
def view_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    # Ensure the resume belongs to the current user
    if resume.user_id != current_user.id:
        flash('You do not have permission to view this resume')
        return redirect(url_for('main.dashboard'))

    return render_template('results.html', resume=resume)
