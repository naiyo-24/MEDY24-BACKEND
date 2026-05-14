from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
import jwt
import os
from datetime import datetime, timedelta

from db import get_db
from models.auth.customer_user_models import CustomerUser
from services.auth.customer.customer_id_generator import generate_customer_id
from services.auth.customer.profile_photo_upload import upload_profile_photo

try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

# Pydantic Request Models
class PhoneCheckRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number to check")

class SendOTPRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number to send OTP to")

class AddressInput(BaseModel):
    address: str
    type: str = Field(default="home", description="Address type: home, office, other")

class VerifyOTPRequest(BaseModel):
    token: str = Field(..., description="Firebase ID token")
    phone_number: str = Field(..., description="Phone number")
    full_name: Optional[str] = Field(None, description="Full name (required for signup)")
    email: Optional[str] = Field(None, description="Email address")
    alternative_phone_no: Optional[str] = Field(None, description="Alternative phone number")
    saved_addresses: Optional[List[dict]] = Field(None, description="List of saved addresses")

router = APIRouter(prefix="/customers", tags=["Customer Auth"])


@router.post("/check-phone")
async def check_phone(
    request: PhoneCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check if a phone number is registered in the system
    """
    phone_number = request.phone_number.replace(" ", "").replace("-", "")
    
    # Ensure phone has country code
    if not phone_number.startswith("+"):
        phone_number = "+91" + phone_number.lstrip("0")
    
    user = db.query(CustomerUser).filter(CustomerUser.phone_number == phone_number).first()
    
    return {
        "message": "Phone check completed",
        "phone_number": phone_number,
        "exists": user is not None,
        "user_id": user.customer_id if user else None
    }


@router.post("/send-otp")
async def send_otp(
    request: SendOTPRequest
):
    """
    Trigger OTP sending to the customer's phone number.
    NOTE: The actual OTP is sent by Firebase from the client-side.
    This endpoint verifies the phone number format and returns a confirmation.
    """
    phone_number = request.phone_number.replace(" ", "").replace("-", "")
    
    if not phone_number or len(phone_number) < 10:
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    
    # Ensure phone number has country code
    if not phone_number.startswith("+"):
        phone_number = "+91" + phone_number.lstrip("0")
    
    return {
        "message": "OTP will be sent to your phone",
        "phone_number": phone_number,
        "instruction": "Enter the OTP received on your phone number"
    }


@router.post("/verify-otp")
async def verify_otp(
    token: str = Form(...),
    phone_number: str = Form(...),
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    alternative_phone_no: Optional[str] = Form(None),
    profile_photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Verify Firebase ID token and authenticate user.
    
    For new users (signup):
        - Requires: token, phone_number, full_name
        - Optional: email, alternative_phone_no, profile_photo
    
    For existing users (login):
        - Requires: token, phone_number
    """
    
    if not FIREBASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Firebase not configured")
    
    try:
        # Verify the Firebase ID token
        decoded_token = firebase_auth.verify_id_token(token)
        firebase_phone = decoded_token.get("phone_number", "")
        
        # Normalize both phone numbers for comparison
        # Remove spaces and dashes
        firebase_phone_normalized = firebase_phone.replace(" ", "").replace("-", "")
        phone_normalized = phone_number.replace(" ", "").replace("-", "")
        
        # Ensure incoming phone has country code (+91 for India)
        if not phone_normalized.startswith("+"):
            phone_normalized = "+91" + phone_normalized.lstrip("0")
        
        # Compare normalized versions
        if firebase_phone_normalized != phone_normalized:
            raise HTTPException(
                status_code=401, 
                detail=f"Phone number mismatch. Token: {firebase_phone_normalized}, Provided: {phone_normalized}"
            )
        
        # Store the normalized phone number for database
        phone_number = phone_normalized
        
        # Check if user exists
        user = db.query(CustomerUser).filter(
            CustomerUser.phone_number == phone_number
        ).first()
        
        if user:
            # LOGIN FLOW: User exists
            backend_token = generate_backend_token(user.customer_id)
            
            return {
                "message": "Login successful",
                "status": "login",
                "user": user.to_dict(),
                "backend_token": backend_token
            }
        
        else:
            # SIGNUP FLOW: New user
            if not full_name or full_name.strip() == "":
                raise HTTPException(
                    status_code=400, 
                    detail="Full name is required for new user registration"
                )
            
            # Generate customer ID
            customer_id = generate_customer_id()
            
            # Upload profile photo if provided
            profile_photo_url = None
            if profile_photo:
                try:
                    profile_photo_url = upload_profile_photo(profile_photo, customer_id)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Failed to upload photo: {str(e)}")
            
            # Create new customer user
            new_user = CustomerUser(
                customer_id=customer_id,
                phone_number=phone_number,
                full_name=full_name.strip(),
                email=email,
                alternative_phone_no=alternative_phone_no,
                saved_addresses=[],
                profile_photo=profile_photo_url
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Generate backend token
            backend_token = generate_backend_token(new_user.customer_id)
            
            return {
                "message": "Registration successful",
                "status": "signup",
                "user": new_user.to_dict(),
                "backend_token": backend_token
            }
    
    except HTTPException as e:
        # Re-raise HTTP exceptions as-is (401, 400, 404, etc.)
        raise e
    except firebase_admin.exceptions.FirebaseError as e:
        raise HTTPException(
            status_code=401, 
            detail=f"Invalid Firebase token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authorization error: {str(e)}")


@router.get("/profile/{customer_id}")
async def get_profile(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """
    Get customer profile by customer ID
    """
    user = db.query(CustomerUser).filter(CustomerUser.customer_id == customer_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return {
        "message": "Profile retrieved successfully",
        "user": user.to_dict()
    }


@router.put("/profile/{customer_id}")
async def update_profile(
    customer_id: str,
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    alternative_phone_no: Optional[str] = Form(None),
    profile_photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Update customer profile information
    """
    user = db.query(CustomerUser).filter(CustomerUser.customer_id == customer_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Update full name if provided
    if full_name and full_name.strip():
        user.full_name = full_name.strip()
    
    # Update email if provided
    if email:
        user.email = email
    
    # Update alternative phone number if provided
    if alternative_phone_no:
        user.alternative_phone_no = alternative_phone_no
    
    # Update profile photo if provided
    if profile_photo:
        try:
            new_photo_url = upload_profile_photo(profile_photo, customer_id)
            user.profile_photo = new_photo_url
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to upload photo: {str(e)}")
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Profile updated successfully",
        "user": user.to_dict()
    }


@router.post("/addresses/{customer_id}")
async def add_address(
    customer_id: str,
    address_data: AddressInput,
    db: Session = Depends(get_db)
):
    """
    Add a new address to customer's saved addresses
    
    address_type can be: home, office, other
    """
    user = db.query(CustomerUser).filter(CustomerUser.customer_id == customer_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Initialize saved_addresses if None
    if user.saved_addresses is None:
        user.saved_addresses = []
    
    # Create new address entry
    new_address = {
        "id": len(user.saved_addresses) + 1,
        "address": address_data.address,
        "type": address_data.type,
        "created_at": datetime.utcnow().isoformat()
    }
    
    user.saved_addresses.append(new_address)
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Address added successfully",
        "address": new_address,
        "user": user.to_dict()
    }


@router.delete("/addresses/{customer_id}/{address_id}")
async def delete_address(
    customer_id: str,
    address_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a saved address by address ID
    """
    user = db.query(CustomerUser).filter(CustomerUser.customer_id == customer_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if not user.saved_addresses:
        raise HTTPException(status_code=404, detail="No addresses found")
    
    # Find and remove the address
    user.saved_addresses = [addr for addr in user.saved_addresses if addr.get("id") != address_id]
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Address deleted successfully",
        "user": user.to_dict()
    }


def generate_backend_token(customer_id: str) -> str:
    """
    Generate a JWT token for backend authentication
    """
    secret_key = os.getenv("JWT_SECRET", "your-secret-key")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    
    payload = {
        "customer_id": customer_id,
        "exp": datetime.utcnow() + timedelta(days=30),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token
