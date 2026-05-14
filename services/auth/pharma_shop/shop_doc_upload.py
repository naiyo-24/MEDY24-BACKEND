import os
from PIL import Image
import shutil
from fastapi import UploadFile

UPLOAD_DIR = "uploads/pharma_shop"

def save_and_compress_file(file: UploadFile, shop_id: str, field_name: str) -> str:
    """
    Upload and compress/save file for pharma shop
    
    Args:
        file: UploadFile object
        shop_id: Shop ID
        field_name: Parameter name for the file
    
    Returns:
        str: File path of the uploaded file
    """
    # Create directory if not exists
    target_dir = os.path.join(UPLOAD_DIR, shop_id, field_name)
    os.makedirs(target_dir, exist_ok=True)
    
    # Get extension
    ext = os.path.splitext(file.filename)[1].lower()
    if not ext:
        # Fallback for some browsers/files
        ext = ".jpg"
        
    filename = f"{field_name}{ext}"
    file_path = os.path.join(target_dir, filename)
    
    # Check if it's an image for compression
    if ext in ['.jpg', '.jpeg', '.png', '.webp']:
        try:
            img = Image.open(file.file)
            # Convert to RGB if necessary (e.g. for PNG to JPEG)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Save with compression
            img.save(file_path, optimize=True, quality=70)
        except Exception as e:
            # If compression fails, save as is
            print(f"Compression failed for {filename}: {e}")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
    else:
        # For PDF and other files, save as is
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    return file_path

def delete_file(file_path: str) -> bool:
    """
    Delete a file from uploads directory
    
    Args:
        file_path: Path to the file to delete
    
    Returns:
        bool: True if successful, False otherwise
    """
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            # Try to remove the directory if it's empty
            parent_dir = os.path.dirname(file_path)
            if not os.listdir(parent_dir):
                os.rmdir(parent_dir)
                # Try to remove parent of parent if empty
                grandparent_dir = os.path.dirname(parent_dir)
                if not os.listdir(grandparent_dir):
                    os.rmdir(grandparent_dir)
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    return True
