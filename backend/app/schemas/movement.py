from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.movement import MovementType

class MovementOut(BaseModel):
    id: int
    movement_type: MovementType
    product_id: int
    location_id: int
    quantity: float
    reference: str
    reference_id: Optional[int]
    notes: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    model_config = {'from_attributes': True}
