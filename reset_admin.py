from app import db, create_app
from models import User
from werkzeug.security import generate_password_hash

def reset_admin_password():
    """Reset admin password to use SHA-256 hashing"""
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            # Reset admin password to 'admin123' using sha256
            admin.password_hash = generate_password_hash('admin123', method='sha256')
            db.session.commit()
            print(f"Successfully reset admin password to 'admin123'")
        else:
            print("Admin user not found")

if __name__ == "__main__":
    reset_admin_password()