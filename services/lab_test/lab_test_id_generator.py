import time

def generate_test_id(lab_id: str) -> str:
    """
    Generate a test ID in the pattern: {lab_id}-TEST-{timestamp_in_milliseconds}
    
    Args:
        lab_id (str): The laboratory ID
    
    Returns:
        str: Generated test ID
    """
    timestamp = int(time.time() * 1000)
    return f"{lab_id}-TEST-{timestamp}"
