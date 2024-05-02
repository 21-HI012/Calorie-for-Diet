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

    if not email or not password:
        message = '이메일과 비밀번호를 입력해주세요.'
        return render_template('auth/login.html', message=message)

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        message = '이메일 주소 또는 비밀번호가 올바르지 않습니다.'
        return render_template('auth/login.html', message=message)

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

    if not name or not email or not password:
        message = '이름, 이메일, 비밀번호는 필수 입력 항목입니다.'
        return render_template('auth/signup.html', message=message)

    user = User.query.filter_by(email=email).first()

    if user:
        email_message = '이미 존재하는 이메일 주소입니다.'
        return render_template('auth/signup.html', email_message=email_message)

    if gender == "남자":
        gender = 0
    else:
        gender = 1

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'), gender=gender)

    db.session.add(new_user)
    db.session.commit()

    message = '회원가입 완료! 로그인 해주세요.'
    return render_template('auth/login.html', message=message)