import time

def generate_package_id(lab_id: str) -> str:
    """
    Generate a package ID in the pattern: {lab_id}-PACKAGE-{timestamp_in_milliseconds}
    
    Args:
        lab_id (str): The laboratory ID
    
    Returns:
        str: Generated package ID
    """
    timestamp = int(time.time() * 1000)
    return f"{lab_id}-PACKAGE-{timestamp}"
