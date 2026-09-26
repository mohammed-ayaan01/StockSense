from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.delivery import DeliveryStatus

class DeliveryLineCreate(BaseModel):
    product_id: int
    requested_qty: float

class DeliveryLineOut(BaseModel):
    id: int
    product_id: int
    requested_qty: float
    delivered_qty: float
    model_config = {'from_attributes': True}

class DeliveryCreate(BaseModel):
    customer: Optional[str] = None
    location_id: int
    notes: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    lines: List[DeliveryLineCreate]

class DeliveryOut(BaseModel):
    id: int
    reference: str
    customer: Optional[str]
    location_id: int
    status: DeliveryStatus
    notes: Optional[str]
    scheduled_date: Optional[datetime]
    done_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    lines: List[DeliveryLineOut] = []
    model_config = {'from_attributes': True}
