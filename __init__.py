from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from .config import DevelopmentConfig
from dotenv import load_dotenv
import os
# from flask_socketio import SocketIO
from .extension import db, socketio

from .main import home as home_blueprint
from .auth import auth as auth_blueprint
from .user import user as user_blueprint
from .cam import cam as cam_blueprint
from .record import record as record_blueprint
from .detection import barcode as barcode_blueprint
from .food import food as food_blueprint

from .auth.models import User

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://root:{os.getenv('MYSQL_ROOT_PASSWORD')}@db:3306/{os.getenv('MYSQL_DATABASE')}"
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    Migrate(app, db)
    socketio.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(home_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(cam_blueprint)
    app.register_blueprint(record_blueprint)
    app.register_blueprint(barcode_blueprint)
    app.register_blueprint(food_blueprint)

    return app
