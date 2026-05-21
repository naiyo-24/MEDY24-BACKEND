import os
import shutil
from fastapi import UploadFile
from datetime import datetime


async def upload_prescription(
    booking_id: str,
    file: UploadFile,
    upload_dir: str = "uploads/lab_tests"
) -> str:
    """
    Upload prescription/report file for a booking.
    
    Args:
        booking_id: Unique booking ID
        file: UploadFile object
        upload_dir: Directory to store uploads
    
    Returns:
        file_url: Path to uploaded file
    """
    try:
        # Create booking-specific directory if it doesn't exist
        booking_upload_dir = os.path.join(upload_dir, booking_id)
        os.makedirs(booking_upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        new_filename = f"report_{timestamp}{file_extension}"
        
        file_path = os.path.join(booking_upload_dir, new_filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return relative URL path
        file_url = f"/uploads/lab_tests/{booking_id}/{new_filename}"
        return file_url
    
    except Exception as e:
        raise Exception(f"Error uploading prescription: {str(e)}")


async def upload_multiple_prescriptions(
    booking_id: str,
    files: list,
    upload_dir: str = "uploads/lab_tests"
) -> list:
    """
    Upload multiple prescription/report files for a booking.
    
    Args:
        booking_id: Unique booking ID
        files: List of UploadFile objects
        upload_dir: Directory to store uploads
    
    Returns:
        file_urls: List of paths to uploaded files
    """
    file_urls = []
    
    for file in files:
        try:
            file_url = await upload_prescription(booking_id, file, upload_dir)
            file_urls.append(file_url)
        except Exception as e:
            print(f"Error uploading file {file.filename}: {str(e)}")
    
    return file_urls
