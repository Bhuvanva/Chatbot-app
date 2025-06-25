from datetime import datetime
from typing import Optional
from .base import BaseSchema

class TestPricingBase(BaseSchema):
    test_name_id: Optional[int] = None
    lab_vendor_id: Optional[int] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    is_available: Optional[bool] = None

class TestPricingCreate(TestPricingBase):
    test_name_id: int
    lab_vendor_id: int
    price: float

class TestPricingUpdate(TestPricingBase):
    pass

class TestPricingInDB(TestPricingBase):
    id: int
    created_at: datetime
    isDeleted: bool

class TestPricingResponse(TestPricingBase):
    id: int
    created_at: datetime
    isDeleted: bool 