from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from .config import DevelopmentConfig
from dotenv import load_dotenv
import os
from flask_socketio import SocketIO

load_dotenv()
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://root:{os.getenv('MYSQL_ROOT_PASSWORD')}@db:3306/{os.getenv('MYSQL_DATABASE')}"
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    migrate = Migrate(app, db)

    socketio.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint)

    from .cam import cam as cam_blueprint
    app.register_blueprint(cam_blueprint)

    from .upload_s3 import upload as upload_blueprint
    app.register_blueprint(upload_blueprint)

    return app
