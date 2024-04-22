from flask import render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from .models import User
from ..extension import db
from . import auth

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home.intro'))


@auth.route('/login')
def login():
    return render_template('auth/login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user)
    return redirect(url_for('home.main'))


@auth.route('/signup')
def signup():
    return render_template('auth/signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    gender = request.form.get('gender')
    
    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    if gender == "남자":
        gender = 0
    else:
        gender = 1

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'), gender=gender)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))