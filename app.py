import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    # Create the app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configure the database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/crisis_db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # File upload configuration
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader for Flask-Login
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from auth import auth_bp
    from user import user_bp
    from rescue import rescue_bp
    from admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(rescue_bp, url_prefix='/rescue')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Main route
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    # Create database tables
    with app.app_context():
        import models  # noqa: F401
        db.create_all()
        
        # Create default admin user if it doesn't exist
        from models import User
        from werkzeug.security import generate_password_hash
        
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@crisis.system',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                full_name='System Administrator'
            )
            db.session.add(admin_user)
            db.session.commit()
            app.logger.info("Default admin user created: admin / admin123")
    
    return app

# Create app instance
app = create_app()
