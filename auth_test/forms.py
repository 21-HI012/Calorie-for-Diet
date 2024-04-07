from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')