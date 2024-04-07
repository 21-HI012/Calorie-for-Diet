from flask import Blueprint, render_template, redirect, url_for, flash
from . import auth
from .forms import LoginForm, RegisterForm
from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('New user has been created!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                flash('Login successful!')
                return redirect(url_for('index'))
            else:
                flash('Invalid login attempt.')
    return render_template('login.html', form=form)


# @auth.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('home.intro'))

# @auth.route('/login')
# def login():
#     return render_template('auth/login.html')

# @auth.route('/login', methods=['POST'])
# def login_post():
#     email = request.form.get('email')
#     password = request.form.get('password')
#     # remember = True if request.form.get('remember') else False

#     user = User.query.filter_by(email=email).first()

#     if not user or not check_password_hash(user.password, password):
#         flash('Please check your login details and try again.')
#         return redirect(url_for('auth.login'))

#     login_user(user)
#     return redirect(url_for('home.main'))

# @auth.route('/signup')
# def signup():
#     return render_template('auth/signup.html')



# @auth.route('/signup', methods=['POST'])
# def signup_post():
#     email = request.form.get('email')
#     name = request.form.get('name')
#     password = request.form.get('password')
#     gender = request.form.get('gender')
    
#     user = User.query.filter_by(email=email).first()

#     if user:
#         flash('Email address already exists')
#         return redirect(url_for('auth.signup'))

#     if gender == "남자":
#         gender = 0
#     else:
#         gender = 1

#     new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), gender=gender)

#     db.session.add(new_user)
#     db.session.commit()

#     return redirect(url_for('auth.login'))