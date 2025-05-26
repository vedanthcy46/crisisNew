from flask import Blueprint

rescue_bp = Blueprint('rescue', __name__, template_folder='../templates/rescue')

from . import routes
