import os
from PIL import Image
import io
from fastapi import UploadFile

def upload_medicine_photo(file: UploadFile, medicine_id: str, medicine_name: str) -> str:
    """
    Upload and compress medicine photo
    
    Args:
        file: UploadFile object
        medicine_id: Medicine ID
        medicine_name: Medicine name
    
    Returns:
        str: File path of the uploaded image
    """
    # Create directory if it doesn't exist
    upload_dir = f"uploads/medicine/{medicine_id}/{medicine_name}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Get file extension
    file_extension = os.path.splitext(file.filename)[1]
    # Clean medicine name for filename
    clean_medicine_name = "".join([c for c in medicine_name if c.isalnum() or c in (' ', '_', '-')]).strip().replace(' ', '_')
    file_path = f"{upload_dir}/{clean_medicine_name}{file_extension}"
    
    # Read file content
    contents = file.file.read()
    image = Image.open(io.BytesIO(contents))
    
    # Convert to RGB if necessary (for JPEG compression)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    
    # Compress and save
    image.save(file_path, optimize=True, quality=70)
    
    return file_path

def delete_medicine_photo(photo_url: str):
    """
    Delete a medicine photo from uploads directory
    
    Args:
        photo_url: Path to the photo file
    """
    if photo_url and os.path.exists(photo_url):
        try:
            os.remove(photo_url)
            # Try to remove the directory if it's empty
            parent_dir = os.path.dirname(photo_url)
            if not os.listdir(parent_dir):
                os.rmdir(parent_dir)
                # Try to remove parent of parent if empty
                grandparent_dir = os.path.dirname(parent_dir)
                if not os.listdir(grandparent_dir):
                    os.rmdir(grandparent_dir)
        except Exception as e:
            print(f"Error deleting photo: {e}")
