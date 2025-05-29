import os
import base64
from io import BytesIO
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
try:
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client.get_database()
    fs_files = db.fs_files
    fs_chunks = db.fs_chunks
    logger.info("MongoDB connection established")
except Exception as e:
    logger.error(f"MongoDB connection error: {str(e)}")
    db = None

def save_image(file, incident_id=None):
    """
    Save an image to MongoDB
    Returns the MongoDB ObjectId of the saved file
    """
    if db is None:
        logger.error("MongoDB connection not available")
        return None
    
    try:
        # Read file data
        filename = secure_filename(file.filename)
        file_data = file.read()
        content_type = file.content_type
        
        # Create metadata
        metadata = {
            "filename": filename,
            "contentType": content_type,
            "incident_id": str(incident_id) if incident_id else None
        }
        
        # Insert file data
        file_id = fs_files.insert_one({
            "filename": filename,
            "length": len(file_data),
            "chunkSize": 261120,
            "metadata": metadata
        }).inserted_id
        
        # Insert file chunks
        chunk_size = 261120
        for i in range(0, len(file_data), chunk_size):
            chunk_data = file_data[i:i+chunk_size]
            fs_chunks.insert_one({
                "files_id": file_id,
                "n": i // chunk_size,
                "data": chunk_data
            })
        
        logger.info(f"Image saved to MongoDB with ID: {file_id}")
        return str(file_id)
    
    except Exception as e:
        logger.error(f"Error saving image to MongoDB: {str(e)}")
        return None

def get_image(file_id):
    """
    Retrieve an image from MongoDB by its ID
    Returns a tuple of (binary_data, content_type)
    """
    if db is None:
        logger.error("MongoDB connection not available")
        return None, None
    
    try:
        # Get file metadata
        file_doc = fs_files.find_one({"_id": ObjectId(file_id)})
        if not file_doc:
            logger.warning(f"Image with ID {file_id} not found")
            return None, None
        
        # Get content type
        content_type = file_doc.get("metadata", {}).get("contentType", "image/jpeg")
        
        # Get file chunks
        chunks = list(fs_chunks.find({"files_id": ObjectId(file_id)}).sort("n", 1))
        if not chunks:
            logger.warning(f"No chunks found for image with ID {file_id}")
            return None, None
        
        # Combine chunks
        file_data = b''
        for chunk in chunks:
            file_data += chunk["data"]
        
        logger.info(f"Image retrieved from MongoDB with ID: {file_id}")
        return file_data, content_type
    
    except Exception as e:
        logger.error(f"Error retrieving image from MongoDB: {str(e)}")
        return None, None

def get_image_base64(file_id):
    """
    Get image as base64 string for embedding in HTML
    """
    file_data, content_type = get_image(file_id)
    if file_data:
        b64_data = base64.b64encode(file_data).decode('utf-8')
        return f"data:{content_type};base64,{b64_data}"
    return None

def delete_image(file_id):
    """
    Delete an image from MongoDB
    """
    if db is None:
        logger.error("MongoDB connection not available")
        return False
    
    try:
        # Delete file metadata and chunks
        fs_files.delete_one({"_id": ObjectId(file_id)})
        fs_chunks.delete_many({"files_id": ObjectId(file_id)})
        logger.info(f"Image deleted from MongoDB with ID: {file_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error deleting image from MongoDB: {str(e)}")
        return False