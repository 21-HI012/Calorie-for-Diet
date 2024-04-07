from flask import Blueprint, request, current_app, render_template
from werkzeug.utils import secure_filename
from .s3_connector import S3Connector

upload = Blueprint('upload', __name__)

@upload.route('/upload-s3')
def upload_form():
    return render_template('upload_s3.html')

@upload.route('/upload-to-s3', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = secure_filename(file.filename)
        aws_access_key_id = current_app.config['AWS_ACCESS_KEY_ID']
        aws_secret_access_key = current_app.config['AWS_SECRET_ACCESS_KEY']
        s3_bucket_name = current_app.config['S3_BUCKET_NAME']
        
        s3 = S3Connector(aws_access_key_id, aws_secret_access_key, s3_bucket_name)
        response = s3.upload_file_to_s3(file, filename)
        return response
