from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    model_config = {'from_attributes': True}

class UoMCreate(BaseModel):
    name: str
    abbreviation: str

class UoMOut(BaseModel):
    id: int
    name: str
    abbreviation: str
    created_at: datetime
    model_config = {'from_attributes': True}

class ProductCreate(BaseModel):
    name: str
    sku: str
    category_id: int
    uom_id: int
    unit_cost: float = 0.0
    reorder_threshold: Optional[float] = None
    description: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    uom_id: Optional[int] = None
    unit_cost: Optional[float] = None
    reorder_threshold: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ProductOut(BaseModel):
    id: int
    name: str
    sku: str
    category_id: int
    uom_id: int
    unit_cost: float
    reorder_threshold: Optional[float]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryOut] = None
    unit_of_measure: Optional[UoMOut] = None
    model_config = {'from_attributes': True}
