from flask import Blueprint

barcode = Blueprint('barcode', __name__)

from . import barcode_routes