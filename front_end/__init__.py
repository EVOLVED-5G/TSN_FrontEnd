from flask import Blueprint

bp = Blueprint('frontEnd', __name__)

from .routes import *