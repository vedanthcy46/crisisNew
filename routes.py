from flask import Blueprint, send_file, Response
from io import BytesIO
from mongo_utils import get_image

# Create a blueprint for image routes
image_bp = Blueprint('image', __name__)

@image_bp.route('/image/<file_id>')
def serve_image(file_id):
    """Serve images from MongoDB"""
    image_data, content_type = get_image(file_id)
    
    if not image_data:
        return "Image not found", 404
    
    return Response(
        BytesIO(image_data),
        mimetype=content_type,
        direct_passthrough=True
    )