from sqlalchemy import Column, String, JSON, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from db import Base

class TestPackage(Base):
    __tablename__ = "test_packages"

    package_id = Column(String, primary_key=True, index=True)
    lab_id = Column(String, ForeignKey("patho_lab_users.lab_id"), nullable=False, index=True)
    
    package_name = Column(String, nullable=False)
    # Test details JSON structure: ["test_id_1", "test_id_2", ...]
    test_details = Column(JSON, nullable=False)
    
    package_description = Column(String, nullable=True)
    
    package_sample_collection_time = Column(String, nullable=False)  # e.g., "2 days", "24 hours"
    package_report_delivery_time = Column(String, nullable=False)  # e.g., "3 days", "48 hours"
    
    package_market_price = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0, nullable=False)
    package_final_price = Column(Float, nullable=False)  # market_price - (market_price * discount_percentage / 100)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def to_dict(self):
        return {
            "package_id": self.package_id,
            "lab_id": self.lab_id,
            "package_name": self.package_name,
            "test_details": self.test_details,
            "package_description": self.package_description,
            "package_sample_collection_time": self.package_sample_collection_time,
            "package_report_delivery_time": self.package_report_delivery_time,
            "package_market_price": self.package_market_price,
            "discount_percentage": self.discount_percentage,
            "package_final_price": self.package_final_price,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
