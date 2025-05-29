import os
from app import create_app, db
from models import Incident
from mongo_utils import save_image
from werkzeug.datastructures import FileStorage
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment variables
load_dotenv()

def migrate_images_to_mongodb():
    """Migrate existing images from filesystem to MongoDB"""
    app = create_app()
    with app.app_context():
        # First check if image_path column exists
        result = db.session.execute(text("SHOW COLUMNS FROM incidents LIKE 'image_path'"))
        if not result.fetchone():
            print("No image_path column found in incidents table")
            return
            
        # Get all incidents with image paths using raw SQL
        incidents = db.session.execute(text("SELECT id, image_path FROM incidents WHERE image_path IS NOT NULL")).fetchall()
        
        print(f"Found {len(incidents)} incidents with images to migrate")
        
        for incident in incidents:
            try:
                incident_id = incident[0]
                image_path = incident[1]
                
                # Get the file path
                file_path = os.path.join(app.root_path, 'static', 'uploads', image_path)
                
                if os.path.exists(file_path):
                    # Get file name and content type
                    filename = os.path.basename(file_path)
                    content_type = 'image/jpeg'  # Default
                    if filename.lower().endswith('.png'):
                        content_type = 'image/png'
                    elif filename.lower().endswith('.gif'):
                        content_type = 'image/gif'
                    
                    # Create a FileStorage object
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                        file = FileStorage(
                            stream=open(file_path, 'rb'),
                            filename=filename,
                            content_type=content_type
                        )
                        
                        # Save to MongoDB
                        image_id = save_image(file, incident_id)
                        
                        if image_id:
                            # Update incident with MongoDB ID using raw SQL
                            db.session.execute(
                                text("UPDATE incidents SET image_id = :image_id WHERE id = :incident_id"),
                                {"image_id": image_id, "incident_id": incident_id}
                            )
                            print(f"Migrated image for incident #{incident_id}: {filename} -> {image_id}")
                        else:
                            print(f"Failed to migrate image for incident #{incident_id}: {filename}")
                else:
                    print(f"File not found for incident #{incident_id}: {file_path}")
            
            except Exception as e:
                print(f"Error migrating image for incident #{incident_id}: {str(e)}")
        
        # Save changes
        db.session.commit()
        print("Migration completed")

if __name__ == "__main__":
    migrate_images_to_mongodb()