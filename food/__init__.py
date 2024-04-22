from flask import Blueprint

food = Blueprint('food', __name__)

from . import views
