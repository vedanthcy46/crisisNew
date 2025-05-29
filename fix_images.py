from app import create_app, db
from models import Incident
from mongo_utils import save_image
from werkzeug.datastructures import FileStorage
import os
import logging
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def fix_image_display():
    """Fix image display issues by migrating images to MongoDB"""
    app = create_app()
    with app.app_context():
        # Get all incidents with image_path but no image_id using raw SQL
        result = db.session.execute(text(
            "SELECT id, image_path FROM incidents WHERE image_path IS NOT NULL AND (image_id IS NULL OR image_id = '')"
        ))
        incidents = result.fetchall()
        
        print(f"Found {len(incidents)} incidents with image_path but no image_id")
        
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
                    
                    print(f"Processing incident #{incident_id}: {image_path}")
                    
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
                            print(f"  - Successfully migrated image to MongoDB: {image_id}")
                        else:
                            print(f"  - Failed to migrate image to MongoDB")
                else:
                    print(f"File not found for incident #{incident_id}: {file_path}")
            
            except Exception as e:
                print(f"Error migrating image for incident #{incident_id}: {str(e)}")
        
        # Save changes
        db.session.commit()
        print("Migration completed")

if __name__ == "__main__":
    fix_image_display()