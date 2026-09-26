from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.receipt import ReceiptStatus

class ReceiptLineCreate(BaseModel):
    product_id: int
    expected_qty: float

class ReceiptLineOut(BaseModel):
    id: int
    product_id: int
    expected_qty: float
    received_qty: float
    model_config = {'from_attributes': True}

class ReceiptCreate(BaseModel):
    supplier: Optional[str] = None
    location_id: int
    notes: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    lines: List[ReceiptLineCreate]

class ReceiptOut(BaseModel):
    id: int
    reference: str
    supplier: Optional[str]
    location_id: int
    status: ReceiptStatus
    notes: Optional[str]
    scheduled_date: Optional[datetime]
    done_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    lines: List[ReceiptLineOut] = []
    model_config = {'from_attributes': True}
