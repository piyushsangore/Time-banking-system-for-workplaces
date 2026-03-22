import re

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.user_model import UserModel


auth_bp = Blueprint('auth', __name__)

EMAIL_PATTERN = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not name or not email or not password:
        flash('Name, email, and password are required.', 'danger')
        return redirect(url_for('auth.register'))

    if not EMAIL_PATTERN.match(email):
        flash('Please enter a valid email address.', 'danger')
        return redirect(url_for('auth.register'))

    if password != confirm_password:
        flash('Password and Confirm Password must match.', 'danger')
        return redirect(url_for('auth.register'))

    existing_user = UserModel.find_user_by_email(email)
    if existing_user:
        flash('An account with this email already exists.', 'danger')
        return redirect(url_for('auth.register'))

    user = UserModel.create_user(name=name, email=email, password=password)
    session['user_id'] = str(user._id)
    flash('Registration successful.', 'success')

    return redirect(url_for('tasks.dashboard'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    if not email or not password:
        flash('Email and password are required.', 'danger')
        return redirect(url_for('auth.login'))

    user = UserModel.find_user_by_email(email)
    if not user or not user.verify_password(password):
        flash('Invalid email or password.', 'danger')
        return redirect(url_for('auth.login'))

    session['user_id'] = str(user._id)
    return redirect(url_for('tasks.dashboard'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
