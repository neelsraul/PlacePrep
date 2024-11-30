import os
import pickle
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import db, login_manager
from blueprints.auth import auth_blueprint
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from PyPDF2 import PdfReader
from docx import Document

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the trained model and vectorizer
MODEL_PATH = 'models/rf_classifier_job_recommendation.pkl'
VECTORIZER_PATH = 'models/tfidf_vectorizer_job_recommendation.pkl'

try:
    with open(MODEL_PATH, 'rb') as model_file:
        job_recommender_model = pickle.load(model_file)

    with open(VECTORIZER_PATH, 'rb') as vectorizer_file:
        tfidf_vectorizer = pickle.load(vectorizer_file)

    logging.info("Model and vectorizer loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model or vectorizer: {e}")
    job_recommender_model = None
    tfidf_vectorizer = None

# Flask application instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'neelsraul'
app.config.from_object(Config)

# Initialize extensions with the app
db.init_app(app)
login_manager.init_app(app)
migrate = Migrate(app, db)

# Register the auth blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

# Import models after initializing db and login_manager to avoid circular import
with app.app_context():
    from models.user import User
    from models.resume import Resume
    db.create_all()
    logging.info("Database tables created successfully.")

# Create necessary folders if not present
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
    logging.info(f"Upload folder created at: {app.config['UPLOAD_FOLDER']}")

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    logging.info(f"Loaded user: {user.username if user else 'None'}")
    return user

### HELPER FUNCTIONS ###
def extract_text_from_pdf(filepath):
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(filepath)
        text = ''.join(page.extract_text() for page in reader.pages if page.extract_text())
        logging.info("Text successfully extracted from PDF.")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        raise ValueError("Failed to extract text from PDF file.")

def extract_text_from_docx(filepath):
    """Extract text from a DOCX file."""
    try:
        doc = Document(filepath)
        text = '\n'.join(paragraph.text for paragraph in doc.paragraphs)
        logging.info("Text successfully extracted from DOCX.")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from DOCX: {e}")
        raise ValueError("Failed to extract text from DOCX file.")

### ROUTES ###

@app.route('/')
def home():
    logging.info("Rendering home page.")
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    logging.info(f"User {current_user.username} accessed dashboard with {len(resumes)} resumes.")
    return render_template('dashboard.html', user=current_user, resumes=resumes)

@app.route('/view_resume/<int:resume_id>')
@login_required
def view_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        logging.warning(f"Unauthorized access attempt for resume {resume_id} by user {current_user.username}.")
        return redirect(url_for('dashboard'))
    
    recommendation = resume.recommendations
    logging.info(f"Displaying recommendation for resume {resume_id}: {recommendation}")
    
    # Define quiz paths
    quiz_paths = {
        'Machine Learning Engineer': 'machine_learning',
        'Backend Developer': 'backend_developer',
        'Data Analyst': 'data_analyst'
    }

    quiz_url = url_for(quiz_paths.get(recommendation, 'dashboard'))
    return render_template('results.html', resume=resume, recommendation=recommendation, quiz_url=quiz_url)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_resume():
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file selected!', 'danger')
            logging.warning("Upload failed: No file selected.")
            return redirect(request.url)

        file = request.files['resume']
        if file.filename == '':
            flash('No file selected!', 'danger')
            logging.warning("Upload failed: Empty file name.")
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            logging.info(f"Resume file saved at {filepath}.")

            try:
                # Detect file type and extract text
                if filename.lower().endswith('.pdf'):
                    resume_text = extract_text_from_pdf(filepath)
                elif filename.lower().endswith('.docx'):
                    resume_text = extract_text_from_docx(filepath)
                else:
                    raise ValueError("Unsupported file format.")

                # Predict job recommendations
                if job_recommender_model and tfidf_vectorizer:
                    transformed_text = tfidf_vectorizer.transform([resume_text])
                    recommendation = job_recommender_model.predict(transformed_text)[0]

                    # Log the recommendation
                    logging.info(f"Recommendation generated: {recommendation}")

                    # Save recommendation in database
                    resume = Resume(
                        user_id=current_user.id,
                        filename=filename,
                        recommendations=recommendation
                    )
                    db.session.add(resume)
                    db.session.commit()

                    # Redirect to results page
                    return redirect(url_for('view_resume', resume_id=resume.id))
                else:
                    raise Exception("Model or vectorizer is not loaded.")
            except Exception as e:
                logging.error(f"Error analyzing resume: {e}")
                flash('An error occurred while analyzing the resume.', 'danger')
                return redirect(request.url)

    logging.info("Rendering upload page.")
    return render_template('upload.html')

# Role-specific pages
@app.route('/machine_learning')
@login_required
def machine_learning():
    return render_template('Machine Learning Quiz.html')

@app.route('/backend_developer')
@login_required
def backend_developer():
    return render_template('Backend Developer Quiz.html')

@app.route('/data_analyst')
@login_required
def data_analyst():
    return render_template('Data Analyst Quiz.html')

@app.route('/resources')
@login_required
def resources():
    logging.info("Rendering resources page.")
    return render_template('info.html')

@app.route('/logout')
@login_required
def logout():
    logging.info(f"Logging out user: {current_user.username}")
    logout_user()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('home'))

@app.errorhandler(404)
def not_found(error):
    logging.warning("404 Error: Page not found.")
    return render_template('400.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logging.error("500 Error: Internal server error.")
    return render_template('500.html'), 500

# Run the app
if __name__ == '__main__':
    logging.info("Starting Flask app...")
    app.run(debug=True)
