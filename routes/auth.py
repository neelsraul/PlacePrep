import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from models.user import User
from models.resume import Resume  # Import the Resume model
from app import db
from flask_login import login_user, logout_user, login_required, current_user

# Configure Blueprint
auth = Blueprint('auth', __name__)

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        logger.info("Attempting to register user: %s", username)

        # Validate inputs
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            logger.warning("Registration failed: Username '%s' already exists.", username)
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            logger.warning("Registration failed: Email '%s' already registered.", email)
            return redirect(url_for('auth.register'))

        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        logger.info("User '%s' registered successfully.", username)
        return redirect(url_for('auth.login'))

    logger.info("Rendering registration page.")
    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        logger.info("Login attempt for user: %s", username)

        # Find user
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            logger.info("User '%s' logged in successfully.", username)
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            logger.warning("Login failed for user '%s'. Invalid credentials.", username)
            return redirect(url_for('auth.login'))

    logger.info("Rendering login page.")
    return render_template('login.html')


@auth.route('/dashboard')
@login_required
def dashboard():
    """
    Displays the dashboard for the logged-in user.
    """
    try:
        logger.info("Loading dashboard for user: %s", current_user.username)
        resumes = Resume.query.filter_by(user_id=current_user.id).all()
        logger.info("User '%s' has %d resumes.", current_user.username, len(resumes))
        return render_template('dashboard.html', resumes=resumes, user=current_user)
    except Exception as e:
        logger.error("Error loading dashboard for user '%s': %s", current_user.username, str(e))
        flash('An error occurred while loading the dashboard.', 'danger')
        return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    """
    Handles user logout.
    """
    logger.info("Logging out user: %s", current_user.username)
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
