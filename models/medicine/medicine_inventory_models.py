from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from db import Base

class MedicineInventory(Base):
    __tablename__ = "medicine_inventory"

    inventory_medicine_id = Column(String, primary_key=True, index=True)
    medicine_id = Column(String, ForeignKey("core_medicines.medicine_id"), nullable=False, index=True)
    shop_id = Column(String, ForeignKey("pharma_shop_users.shop_id"), nullable=False, index=True)
    discount_percent = Column(Float, default=0, nullable=False)
    final_price = Column(Float, nullable=False)
    status = Column(String, default="in stock", nullable=False)  # out of stock, in stock
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def to_dict(self):
        return {
            "inventory_medicine_id": self.inventory_medicine_id,
            "medicine_id": self.medicine_id,
            "shop_id": self.shop_id,
            "discount_percent": self.discount_percent,
            "final_price": self.final_price,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
