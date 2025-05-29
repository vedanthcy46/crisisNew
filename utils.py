import os
import uuid
from functools import wraps
from flask import current_app, flash, redirect, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    """Decorator to require admin role for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def rescue_team_required(f):
    """Decorator to require rescue_team role for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_rescue_team():
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """Decorator to require user role for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_user():
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function