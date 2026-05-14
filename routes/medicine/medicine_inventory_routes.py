from fastapi import APIRouter, Depends, HTTPException, Form, Query
from sqlalchemy.orm import Session
from typing import Optional
from db import get_db
from models.medicine.medicine_inventory_models import MedicineInventory
from models.medicine.core_medicine_models import CoreMedicine
from models.auth.pharma_shop_user_models import PharmaShopUser
from services.medicine.inventory_medicine_id_generator import generate_inventory_medicine_id

router = APIRouter(prefix="/medicine-inventory", tags=["Medicine Inventory"])

@router.post("/create")
async def create_inventory_medicine(
    medicine_id: str = Form(...),
    shop_id: str = Form(...),
    discount_percent: float = Form(default=0),
    status: Optional[str] = Form(default="in stock"),
    db: Session = Depends(get_db)
):
    """
    Add a medicine to shop inventory
    """
    # Validate medicine exists
    medicine = db.query(CoreMedicine).filter(CoreMedicine.medicine_id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    # Validate shop exists
    shop = db.query(PharmaShopUser).filter(PharmaShopUser.shop_id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    # Check if this medicine is already in the shop's inventory
    existing_inventory = db.query(MedicineInventory).filter(
        MedicineInventory.medicine_id == medicine_id,
        MedicineInventory.shop_id == shop_id
    ).first()
    if existing_inventory:
        raise HTTPException(
            status_code=400,
            detail=f"Medicine '{medicine.medicine_name}' is already in shop inventory"
        )
    
    # Calculate final_price automatically based on MRP and discount
    final_price = medicine.mrp - (medicine.mrp * discount_percent / 100)
    
    # Generate inventory medicine ID
    inventory_medicine_id = generate_inventory_medicine_id(medicine_id, shop_id)
    
    # Create inventory record
    new_inventory = MedicineInventory(
        inventory_medicine_id=inventory_medicine_id,
        medicine_id=medicine_id,
        shop_id=shop_id,
        discount_percent=discount_percent,
        final_price=final_price,
        status=status if status in ["in stock", "out of stock"] else "in stock"
    )
    
    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)
    
    return new_inventory.to_dict()

@router.get("/get-all-by-shop/{shop_id}")
async def get_inventory_by_shop(
    shop_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all medicines in shop inventory with pagination and core medicine details
    """
    # Validate shop exists
    shop = db.query(PharmaShopUser).filter(PharmaShopUser.shop_id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    offset = (page - 1) * limit
    inventory_items = db.query(MedicineInventory).filter(
        MedicineInventory.shop_id == shop_id
    ).offset(offset).limit(limit).all()
    
    total = db.query(MedicineInventory).filter(
        MedicineInventory.shop_id == shop_id
    ).count()
    
    # Enrich inventory data with core medicine details
    enriched_data = []
    for item in inventory_items:
        medicine = db.query(CoreMedicine).filter(CoreMedicine.medicine_id == item.medicine_id).first()
        item_dict = item.to_dict()
        if medicine:
            item_dict["medicine_details"] = {
                "medicine_name": medicine.medicine_name,
                "medicine_category": medicine.medicine_category,
                "medicine_photo": medicine.medicine_photo,
                "medicine_quantity": medicine.medicine_quantity,
                "medicine_description": medicine.medicine_description,
                "medicine_composition": medicine.medicine_composition,
                "mrp": medicine.mrp
            }
        enriched_data.append(item_dict)
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "shop_id": shop_id,
        "data": enriched_data
    }

@router.put("/update-by/{inventory_medicine_id}")
async def update_inventory_medicine(
    inventory_medicine_id: str,
    discount_percent: Optional[float] = Form(None),
    status: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Update medicine in inventory. Final price is calculated automatically from MRP and discount.
    """
    inventory_item = db.query(MedicineInventory).filter(
        MedicineInventory.inventory_medicine_id == inventory_medicine_id
    ).first()
    
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Get the medicine to calculate final_price if discount_percent is updated
    medicine = db.query(CoreMedicine).filter(CoreMedicine.medicine_id == inventory_item.medicine_id).first()
    
    # Update fields
    if discount_percent is not None:
        inventory_item.discount_percent = discount_percent
        # Recalculate final_price based on new discount
        if medicine:
            inventory_item.final_price = medicine.mrp - (medicine.mrp * discount_percent / 100)
    
    if status is not None:
        if status in ["in stock", "out of stock"]:
            inventory_item.status = status
        else:
            raise HTTPException(
                status_code=400,
                detail="Status must be either 'in stock' or 'out of stock'"
            )
    
    db.commit()
    db.refresh(inventory_item)
    
    return inventory_item.to_dict()

@router.delete("/delete-by/{inventory_medicine_id}")
async def delete_inventory_medicine(
    inventory_medicine_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete medicine from shop inventory
    """
    inventory_item = db.query(MedicineInventory).filter(
        MedicineInventory.inventory_medicine_id == inventory_medicine_id
    ).first()
    
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    db.delete(inventory_item)
    db.commit()
    
    return {"message": "Medicine removed from inventory successfully"}
