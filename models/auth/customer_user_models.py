from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from db import Base


class CustomerUser(Base):
    __tablename__ = "customer_users"

    customer_id = Column(String, primary_key=True, index=True)
    phone_number = Column(String, unique=True, nullable=False, index=True)
    alternative_phone_no = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    profile_photo = Column(String, nullable=True)
    saved_addresses = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "phone_number": self.phone_number,
            "alternative_phone_no": self.alternative_phone_no,
            "full_name": self.full_name,
            "email": self.email,
            "profile_photo": self.profile_photo,
            "saved_addresses": self.saved_addresses,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
