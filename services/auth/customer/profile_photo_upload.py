import os
import shutil
from fastapi import UploadFile


def upload_profile_photo(profile_photo: UploadFile, customer_id: str) -> str:
    """
    Upload customer profile photo to the uploads folder
    
    Args:
        profile_photo: The uploaded file
        customer_id: Customer ID for naming the folder
    
    Returns:
        str: URL path to the uploaded photo
    """
    try:
        # Create customer upload directory
        upload_dir = f"uploads/auth/{customer_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with customer_id as filename
        file_extension = profile_photo.filename.split('.')[-1]
        file_path = f"{upload_dir}/profile_photo.{file_extension}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(profile_photo.file, buffer)
        
        # Return relative URL path
        return f"/uploads/auth/{customer_id}/profile_photo.{file_extension}"
    
    except Exception as e:
        print(f"Error uploading profile photo: {e}")
        raise Exception(f"Failed to upload profile photo: {str(e)}")


def delete_profile_photo(photo_path: str) -> bool:
    """
    Delete customer profile photo
    
    Args:
        photo_path: Path to the photo file
    
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting profile photo: {e}")
        return False
