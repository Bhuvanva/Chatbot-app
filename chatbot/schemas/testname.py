from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class LabVendorPricing(BaseModel):
    lab_name: Optional[str] = None
    name: Optional[str] = None
    labbuddy_share: Optional[int] = 0
    vendor_discount: Optional[int] = 0
    vendor_price: Optional[int] = 0
    lb_app_price: Optional[int] = 0
    lab_type: Optional[str] = None

class TestNameBase(BaseModel):
    name: Optional[str] = None
    detailed_description: Optional[str] = None
    fasting_required: Optional[int] = None
    fasting_time: Optional[str] = None
    report_time: Optional[int] = None
    slot_time_duration: Optional[int] = None

class TestNameCreate(TestNameBase):
    name: str

class TestNameUpdate(TestNameBase):
    pass

class TestNameInDB(TestNameBase):
    id: int
    createdAt: datetime
    isDeleted: bool
    isActive: bool

class TestNameResponse(TestNameBase):
    id: int
    createdAt: datetime
    isDeleted: bool
    isActive: bool
    lab_vendor_ids: List[int] = []
    pricing: List[LabVendorPricing] = [] 