from app import create_app, db
from models import Incident
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_incident_creation():
    """Debug incident creation process"""
    app = create_app()
    with app.app_context():
        try:
            # Check if image_id column exists
            from sqlalchemy import text
            result = db.session.execute(text("SHOW COLUMNS FROM incidents LIKE 'image_id'"))
            if result.fetchone():
                print("image_id column exists in incidents table")
            else:
                print("image_id column DOES NOT exist in incidents table")
                
            # Create a test incident
            incident = Incident(
                title="Test Incident",
                description="This is a test incident for debugging",
                incident_type="test",
                priority="medium",
                status="pending",
                reported_by=1  # Assuming user ID 1 exists
            )
            
            db.session.add(incident)
            db.session.flush()
            
            # Try to set image_id
            try:
                incident.image_id = "test_image_id"
                print("Successfully set image_id attribute")
            except Exception as e:
                print(f"Error setting image_id attribute: {str(e)}")
                
                # Try with raw SQL
                try:
                    db.session.execute(
                        text("UPDATE incidents SET image_id = :image_id WHERE id = :incident_id"),
                        {"image_id": "test_image_id", "incident_id": incident.id}
                    )
                    print("Successfully set image_id with raw SQL")
                except Exception as e:
                    print(f"Error setting image_id with raw SQL: {str(e)}")
            
            # Commit changes
            db.session.commit()
            print(f"Successfully created test incident with ID: {incident.id}")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during debug: {str(e)}")

if __name__ == "__main__":
    debug_incident_creation()