from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WarehouseCreate(BaseModel):
    name: str
    code: str
    address: Optional[str] = None

class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

class WarehouseOut(BaseModel):
    id: int
    name: str
    code: str
    address: Optional[str]
    is_active: bool
    created_at: datetime
    model_config = {'from_attributes': True}

class LocationCreate(BaseModel):
    warehouse_id: int
    name: str
    code: str
    description: Optional[str] = None

class LocationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class LocationOut(BaseModel):
    id: int
    warehouse_id: int
    name: str
    code: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    warehouse: Optional[WarehouseOut] = None
    model_config = {'from_attributes': True}
