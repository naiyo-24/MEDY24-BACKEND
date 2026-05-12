from sqlalchemy import Column, String, JSON, DateTime, Integer, Float, ForeignKey
from sqlalchemy.sql import func
from db import Base

class TestInventory(Base):
    __tablename__ = "test_inventory"

    test_id = Column(String, primary_key=True, index=True)
    lab_id = Column(String, ForeignKey("patho_lab_users.lab_id"), nullable=False, index=True)
    core_test_id = Column(String, ForeignKey("core_lab_tests.core_test_id"), nullable=False, index=True)
    
    sample_collection_time = Column(String, nullable=False)  # e.g., "2 days", "24 hours"
    report_delivery_time = Column(String, nullable=False)  # e.g., "3 days", "48 hours"
    
    reviews = Column(JSON, nullable=True)  # List of {"customer_id", "customer_name", "customer_phone_no", "comments", "rating"}
    
    price = Column(Float, nullable=False)  # Original price
    discount_percent = Column(Float, default=0, nullable=False)  # Discount percentage
    market_price = Column(Float, nullable=False)  # Price after discount: price - (price * discount_percent / 100)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def to_dict(self):
        return {
            "test_id": self.test_id,
            "lab_id": self.lab_id,
            "core_test_id": self.core_test_id,
            "sample_collection_time": self.sample_collection_time,
            "report_delivery_time": self.report_delivery_time,
            "reviews": self.reviews,
            "price": self.price,
            "discount_percent": self.discount_percent,
            "market_price": self.market_price,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
