import time


def generate_booking_id():
    """
    Generate a unique booking ID with pattern: BOOKING-TIMESTAMP
    Example: BOOKING-1778920685126
    """
    timestamp = int(time.time() * 1000)  # Milliseconds for uniqueness
    booking_id = f"BOOKING-{timestamp}"
    return booking_id
