from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class InventoryStockOut(BaseModel):
    id: int
    product_id: int
    location_id: int
    quantity: float
    reserved: float
    free_to_use: float
    updated_at: datetime
    model_config = {'from_attributes': True}

    @classmethod
    def from_orm_with_computed(cls, obj):
        data = {
            'id': obj.id,
            'product_id': obj.product_id,
            'location_id': obj.location_id,
            'quantity': obj.quantity,
            'reserved': obj.reserved,
            'free_to_use': obj.quantity - obj.reserved,
            'updated_at': obj.updated_at,
        }
        return cls(**data)
