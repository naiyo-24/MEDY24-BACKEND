from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from db import get_db
from models.lab_test.test_package_booking_models import TestPackageBooking
from models.auth.customer_user_models import CustomerUser
from models.auth.patho_lab_user_models import PathoLabUser
from services.lab_test.booking_id_generator import generate_booking_id
from services.razorpay.razorpay_services import client as razorpay_client

router = APIRouter(prefix="/test-package-bookings", tags=["Test Package Bookings"])


# =====================================================
# PYDANTIC MODELS FOR REQUEST/RESPONSE
# =====================================================

class CreateBookingRequest(BaseModel):
    customer_id: str
    lab_id: str
    booking_type: str  # "single_test" or "package"
    booked_items: List[Dict[str, Any]]
    patient_details: List[Dict[str, Any]]
    sample_collection_address: Dict[str, Any]
    sub_total_amount: float
    total_discount_amount: float
    platform_fee: float
    tax_amount: float
    total_amount_to_be_paid: float
    payment_mode: str  # "online" or "cash"
    transaction_id: Optional[str] = None
    transaction_hash: Optional[str] = None
    customer_note: Optional[str] = None


class BookingResponse(BaseModel):
    booking_id: str
    customer_id: str
    lab_id: str
    booking_status: str
    total_amount_to_be_paid: float
    payment_mode: str
    transaction_id: Optional[str]
    transaction_status: str



# =====================================================
# HELPER FUNCTIONS
# =====================================================

def calculate_lab_payable_amount(
    sub_total: float,
    discount: float,
    platform_fee: float,
    tax: float
) -> float:
    """Calculate amount payable to lab after platform fee and discounts"""
    payable = sub_total - discount - platform_fee + tax
    return max(0, payable)


# =====================================================
# 1. POST - CREATE BOOKING
# =====================================================

@router.post("/create-booking", response_model=BookingResponse)
async def create_booking(
    request: CreateBookingRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new lab test or package booking.
    
    - **customer_id**: Customer placing the booking
    - **lab_id**: Pathology lab ID
    - **booking_type**: "single_test" or "package"
    - **payment_mode**: "online" or "cash"
    """
    try:
        # Verify customer exists
        customer = db.query(CustomerUser).filter(
            CustomerUser.customer_id == request.customer_id
        ).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Verify lab exists
        lab = db.query(PathoLabUser).filter(
            PathoLabUser.lab_id == request.lab_id
        ).first()
        if not lab:
            raise HTTPException(status_code=404, detail="Lab not found")
        
        # Generate unique booking ID
        booking_id = generate_booking_id()
        
        # Calculate lab payable amount
        lab_payable_amount = calculate_lab_payable_amount(
            request.sub_total_amount,
            request.total_discount_amount,
            request.platform_fee,
            request.tax_amount
        )
        
        # Prepare gateway response based on payment mode
        gateway_response = {}
        transaction_status = "pending"
        paid_amount = 0.0
        paid_at = None
        transaction_id = None
        
        if request.payment_mode == "online":
            # For online payments, create Razorpay order
            try:
                razorpay_order = razorpay_client.order.create({
                    "amount": int(request.total_amount_to_be_paid * 100),  # Amount in paise
                    "currency": "INR",
                    "receipt": booking_id,
                    "notes": {
                        "booking_id": booking_id,
                        "customer_id": request.customer_id,
                        "lab_id": request.lab_id
                    }
                })
                gateway_response = razorpay_order
                transaction_id = razorpay_order.get("id")
                transaction_status = "initiated"
            except Exception as e:
                print(f"Razorpay error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Payment gateway error: {str(e)}"
                )
        else:
            # For cash payments
            transaction_status = "pending"
            transaction_id = None
        
        # Create booking record
        new_booking = TestPackageBooking(
            booking_id=booking_id,
            customer_id=request.customer_id,
            lab_id=request.lab_id,
            booking_type=request.booking_type,
            booked_items=request.booked_items,
            patient_details=request.patient_details,
            sample_collection_address=request.sample_collection_address,
            booking_status="pending",
            sub_total_amount=request.sub_total_amount,
            total_discount_amount=request.total_discount_amount,
            platform_fee=request.platform_fee,
            tax_amount=request.tax_amount,
            total_amount_to_be_paid=request.total_amount_to_be_paid,
            lab_payable_amount=lab_payable_amount,
            payment_mode=request.payment_mode,
            transaction_id=transaction_id,
            transaction_hash=request.transaction_hash,
            transaction_status=transaction_status,
            gateway_response=gateway_response,
            paid_amount=paid_amount,
            paid_at=paid_at,
            customer_note=request.customer_note,
            report_urls=[]
        )
        
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        
        return BookingResponse(
            booking_id=new_booking.booking_id,
            customer_id=new_booking.customer_id,
            lab_id=new_booking.lab_id,
            booking_status=new_booking.booking_status,
            total_amount_to_be_paid=new_booking.total_amount_to_be_paid,
            payment_mode=new_booking.payment_mode,
            transaction_id=new_booking.transaction_id,
            transaction_status=new_booking.transaction_status
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating booking: {str(e)}")
