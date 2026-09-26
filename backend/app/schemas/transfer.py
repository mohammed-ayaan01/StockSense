from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.transfer import TransferStatus

class TransferLineCreate(BaseModel):
    product_id: int
    quantity: float

class TransferLineOut(BaseModel):
    id: int
    product_id: int
    quantity: float
    model_config = {'from_attributes': True}

class TransferCreate(BaseModel):
    src_location_id: int
    dst_location_id: int
    notes: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    lines: List[TransferLineCreate]

class TransferOut(BaseModel):
    id: int
    reference: str
    src_location_id: int
    dst_location_id: int
    status: TransferStatus
    notes: Optional[str]
    scheduled_date: Optional[datetime]
    done_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    lines: List[TransferLineOut] = []
    model_config = {'from_attributes': True}
