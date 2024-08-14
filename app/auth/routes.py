from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.auth import bp
from app.models import User
from app.forms import LoginForm, SignupForm

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password', 'error')
            current_app.logger.warning(f'Failed login attempt for username: {form.username.data}')
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = SignupForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('Username already exists', 'error')
        else:
            try:
                new_user = User(username=form.username.data, 
                                email=form.email.data, 
                                password_hash=generate_password_hash(form.password.data))
                new_user.generate_token()
                db.session.add(new_user)
                db.session.commit()
                flash('Congratulations, you are now a registered user!', 'success')
                current_app.logger.info(f'New user registered: {new_user.username}')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f'Error during user registration: {str(e)}')
                flash('An error occurred during registration. Please try again.', 'error')
    return render_template('auth/signup.html', title='Register', form=form)

@bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', title='Profile')