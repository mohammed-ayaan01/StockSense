from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.adjustment import AdjustmentStatus

class AdjustmentCreate(BaseModel):
    product_id: int
    location_id: int
    counted_qty: float
    reason: str

class AdjustmentOut(BaseModel):
    id: int
    reference: str
    product_id: int
    location_id: int
    counted_qty: float
    recorded_qty: float
    delta: float
    reason: str
    status: AdjustmentStatus
    done_at: Optional[datetime]
    created_at: datetime
    model_config = {'from_attributes': True}
