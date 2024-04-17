from flask import Blueprint

food = Blueprint('food', __name__)
barcode = Blueprint('barcode', __name__)

from . import food_routes
from . import barcode_routes