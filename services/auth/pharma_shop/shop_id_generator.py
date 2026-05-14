def generate_shop_id(shop_name: str) -> str:
    """
    Generate a unique shop ID based on shop name
    
    Args:
        shop_name: Name of the shop
    
    Returns:
        str: Generated shop ID in format "SHOP-{hash}-{timestamp}"
    """
    import time
    import hashlib
    
    # Create hash from shop name
    name_hash = hashlib.md5(shop_name.encode()).hexdigest()[:4].upper()
    
    # Create timestamp
    timestamp = int(time.time() * 1000)
    
    # Combine to create ID
    shop_id = f"SHOP-{name_hash}-{timestamp}"
    
    return shop_id
