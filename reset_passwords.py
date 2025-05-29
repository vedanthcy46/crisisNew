from app import db, create_app
from models import User
from werkzeug.security import generate_password_hash

def reset_user_passwords():
    """Reset all user passwords to use SHA-256 hashing"""
    app = create_app()
    with app.app_context():
        users = User.query.all()
        updated_count = 0
        
        for user in users:
            # Check if the password hash starts with 'scrypt'
            if user.password_hash.startswith('scrypt'):
                # Reset to a temporary password using sha256
                temp_password = f"temp_{user.username}_123"
                user.password_hash = generate_password_hash(temp_password, method='sha256')
                updated_count += 1
                print(f"Reset password for user: {user.username} (temp password: {temp_password})")
        
        if updated_count > 0:
            db.session.commit()
            print(f"Successfully reset {updated_count} user passwords")
        else:
            print("No passwords needed to be reset")

if __name__ == "__main__":
    reset_user_passwords()