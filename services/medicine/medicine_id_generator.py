def generate_medicine_id(medicine_name: str) -> str:
    """
    Generate a unique medicine ID based on medicine name
    
    Args:
        medicine_name: Name of the medicine
    
    Returns:
        str: Generated medicine ID in format "MED-{timestamp}-{hash}"
    """
    import time
    import hashlib
    
    # Create hash from medicine name
    name_hash = hashlib.md5(medicine_name.encode()).hexdigest()[:4].upper()
    
    # Create timestamp
    timestamp = int(time.time() * 1000)
    
    # Combine to create ID
    medicine_id = f"MED-{name_hash}-{timestamp}"
    
    return medicine_id
