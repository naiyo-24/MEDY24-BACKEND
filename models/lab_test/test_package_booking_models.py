from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    Text
)
from sqlalchemy.sql import func
from sqlalchemy.ext.mutable import MutableList
from db import Base


class TestPackageBooking(Base):
    __tablename__ = "test_package_bookings"

    # =====================================================
    # PRIMARY DETAILS
    # =====================================================

    booking_id = Column(String, primary_key=True, index=True)

    customer_id = Column(
        String,
        ForeignKey("customer_users.customer_id"),
        nullable=False,
        index=True
    )

    lab_id = Column(
        String,
        ForeignKey("patho_lab_users.lab_id"),
        nullable=False,
        index=True
    )

    booking_type = Column(
        String,
        nullable=False
    )
    # single_test / package

    # =====================================================
    # BOOKED ITEMS
    # =====================================================

    booked_items = Column(
        MutableList.as_mutable(JSON),
        nullable=False
    )

    """
    Example:
    [
        {
            "type": "single_test",
            "test_id": "TEST001",
            "test_name": "CBC Test",
            "price": 500
        },
        {
            "type": "package",
            "package_id": "PKG001",
            "package_name": "Full Body Checkup",
            "price": 2500
        }
    ]
    """

    # =====================================================
    # PATIENT DETAILS
    # =====================================================

    patient_details = Column(
        MutableList.as_mutable(JSON),
        nullable=False
    )

    """
    Example:
    [
        {
            "patient_name": "Rajdeep Dey",
            "age": 22,
            "gender": "Male",
            "relation": "Self"
        }
    ]
    """

    # =====================================================
    # ADDRESS DETAILS
    # =====================================================

    sample_collection_address = Column(
        JSON,
        nullable=False
    )

    """
    Example:
    {
        "address_title": "Home",
        "full_address": "Sonarpur, Kolkata",
        "latitude": 22.44,
        "longitude": 88.39,
        "pincode": "700150"
    }
    """

    # =====================================================
    # REPORT DETAILS
    # =====================================================

    report_urls = Column(
        MutableList.as_mutable(JSON),
        nullable=True
    )

    # =====================================================
    # BOOKING STATUS
    # =====================================================

    booking_status = Column(
        String,
        nullable=False,
        default="pending"
    )

    """
    pending
    accepted
    sample_collected
    testing_in_progress
    report_ready
    completed
    cancelled
    """

    cancellation_reason = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # PRICING DETAILS
    # =====================================================

    sub_total_amount = Column(
        Float,
        nullable=False
    )

    total_discount_amount = Column(
        Float,
        default=0,
        nullable=False
    )

    platform_fee = Column(
        Float,
        default=0,
        nullable=False
    )

    tax_amount = Column(
        Float,
        default=0,
        nullable=False
    )

    total_amount_to_be_paid = Column(
        Float,
        nullable=False
    )

    lab_payable_amount = Column(
        Float,
        nullable=False
    )

    # =====================================================
    # PAYMENT DETAILS
    # =====================================================

    payment_mode = Column(
        String,
        nullable=False
    )
    # online / cash

    transaction_id = Column(
        String,
        nullable=True,
        index=True
    )

    transaction_hash = Column(
        String,
        nullable=True
    )

    transaction_status = Column(
        String,
        nullable=False,
        default="pending"
    )

    """
    pending
    initiated
    success
    failed
    refunded
    """

    gateway_response = Column(
        JSON,
        nullable=True
    )

    paid_amount = Column(
        Float,
        default=0,
        nullable=False
    )

    paid_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # =====================================================
    # NOTES
    # =====================================================

    customer_note = Column(
        Text,
        nullable=True
    )

    lab_note = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now()
    )

    # =====================================================
    # RESPONSE METHOD
    # =====================================================

    def to_dict(self):
        return {
            "booking_id": self.booking_id,
            "customer_id": self.customer_id,
            "lab_id": self.lab_id,
            "booking_type": self.booking_type,
            "booked_items": self.booked_items,
            "patient_details": self.patient_details,
            "sample_collection_address": self.sample_collection_address,
            "report_urls": self.report_urls,
            "booking_status": self.booking_status,
            "cancellation_reason": self.cancellation_reason,
            "sub_total_amount": self.sub_total_amount,
            "total_discount_amount": self.total_discount_amount,
            "platform_fee": self.platform_fee,
            "tax_amount": self.tax_amount,
            "total_amount_to_be_paid": self.total_amount_to_be_paid,
            "lab_payable_amount": self.lab_payable_amount,
            "payment_mode": self.payment_mode,
            "transaction_id": self.transaction_id,
            "transaction_hash": self.transaction_hash,
            "transaction_status": self.transaction_status,
            "gateway_response": self.gateway_response,
            "paid_amount": self.paid_amount,
            "paid_at": self.paid_at,
            "customer_note": self.customer_note,
            "lab_note": self.lab_note,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }