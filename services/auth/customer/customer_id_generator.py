import time


def generate_customer_id() -> str:
    """
    Generate a unique customer ID
    
    Returns:
        str: Generated customer ID in format "CUST-{timestamp}"
    """
    timestamp = int(time.time() * 1000)
    return f"CUST-{timestamp}"
