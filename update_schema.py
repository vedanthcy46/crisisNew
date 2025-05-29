from app import create_app, db
from sqlalchemy import text

def update_schema():
    """Update database schema to add image_id column"""
    app = create_app()
    with app.app_context():
        try:
            # Check if column exists
            result = db.session.execute(text("SHOW COLUMNS FROM incidents LIKE 'image_id'"))
            if not result.fetchone():
                # Add image_id column
                db.session.execute(text("ALTER TABLE incidents ADD COLUMN image_id VARCHAR(24)"))
                # Rename image_path to image_id if it exists
                result = db.session.execute(text("SHOW COLUMNS FROM incidents LIKE 'image_path'"))
                if result.fetchone():
                    db.session.execute(text("UPDATE incidents SET image_id = image_path WHERE image_path IS NOT NULL"))
                db.session.commit()
                print("Successfully added image_id column to incidents table")
            else:
                print("image_id column already exists")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating schema: {str(e)}")

if __name__ == "__main__":
    update_schema()