import os
import uuid
from functools import wraps
from flask import current_app, flash, redirect, url_for, abort
from flask_login import current_user
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, subfolder=''):
    """Save uploaded file and return the relative path"""
    if file and allowed_file(file.filename):
        # Generate a unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Create the full upload path
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        # Return relative path for database storage
        return os.path.join(subfolder, unique_filename).replace('\\', '/')
    
    return None

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'error')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def rescue_team_required(f):
    """Decorator to require rescue team role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_rescue_team():
            flash('Access denied. Rescue team privileges required.', 'error')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """Decorator to require user role (regular users only)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_user():
            flash('Access denied. User privileges required.', 'error')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def format_datetime(dt):
    """Format datetime for display"""
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return 'N/A'

def get_status_badge_class(status):
    """Get Bootstrap badge class for status"""
    status_classes = {
        'pending': 'bg-warning',
        'in_progress': 'bg-info',
        'resolved': 'bg-success',
        'closed': 'bg-secondary'
    }
    return status_classes.get(status, 'bg-secondary')

def get_priority_badge_class(priority):
    """Get Bootstrap badge class for priority"""
    priority_classes = {
        'low': 'bg-success',
        'medium': 'bg-warning',
        'high': 'bg-danger',
        'critical': 'bg-dark'
    }
    return priority_classes.get(priority, 'bg-secondary')

def truncate_text(text, length=100):
    """Truncate text to specified length"""
    if len(text) <= length:
        return text
    return text[:length] + '...'
