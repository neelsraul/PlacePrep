from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models.user import User
from models.resume import Resume
from extensions import db

# Create a blueprint for authentication routes
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the user exists
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):  # Ensure check_password exists in your User model
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))  # Ensure 'dashboard' is defined correctly
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Check if the username is already taken
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('auth.register'))

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)  # Make sure this method hashes the password
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_blueprint.route('/logout')
@login_required
def logout():
    """
    Handles user logout.
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@auth_blueprint.route('/dashboard')
@login_required
def dashboard():
    """
    Displays the dashboard for the logged-in user.
    """
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', user=current_user, resumes=resumes)
