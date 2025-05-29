from app import create_app, db
from models import Incident
from mongo_utils import get_image_base64
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_image_display():
    """Debug image display issues"""
    app = create_app()
    with app.app_context():
        # Get all incidents with image_id
        incidents = db.session.query(Incident).filter(Incident.image_id.isnot(None)).all()
        
        print(f"Found {len(incidents)} incidents with image_id")
        
        for incident in incidents:
            print(f"Incident #{incident.id}: image_id={incident.image_id}")
            
            # Try to get image data
            image_data = get_image_base64(incident.image_id)
            if image_data:
                print(f"  - Successfully retrieved image data (length: {len(image_data)})")
            else:
                print(f"  - Failed to retrieve image data")

if __name__ == "__main__":
    debug_image_display()