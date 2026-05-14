def generate_inventory_medicine_id(medicine_id: str, shop_id: str) -> str:
    """
    Generate a unique inventory medicine ID based on medicine_id and shop_id
    
    Args:
        medicine_id: Medicine ID
        shop_id: Shop ID
    
    Returns:
        str: Generated inventory medicine ID in format "INVMED-{timestamp}-{hash}"
    """
    import time
    import hashlib
    
    # Create hash from medicine_id and shop_id combined
    combined = f"{medicine_id}-{shop_id}"
    id_hash = hashlib.md5(combined.encode()).hexdigest()[:4].upper()
    
    # Create timestamp
    timestamp = int(time.time() * 1000)
    
    # Combine to create ID
    inventory_medicine_id = f"INVMED-{id_hash}-{timestamp}"
    
    return inventory_medicine_id
