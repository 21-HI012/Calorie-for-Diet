from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField

class PhotoUploadForm(FlaskForm):
    photo = FileField('사진', validators=[FileAllowed(['jpg', 'png'], '이미지만 업로드 가능합니다.')])
    submit = SubmitField('업로드')