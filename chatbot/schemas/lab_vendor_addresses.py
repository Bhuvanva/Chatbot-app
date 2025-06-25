from datetime import datetime
from typing import Optional
from .base import BaseSchema

class LabVendorAddressBase(BaseSchema):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    lab_vendor_id: Optional[int] = None

class LabVendorAddressCreate(LabVendorAddressBase):
    address: str
    city: str
    state: str
    country: str
    pincode: str
    lab_vendor_id: int

class LabVendorAddressUpdate(LabVendorAddressBase):
    pass

class LabVendorAddressInDB(LabVendorAddressBase):
    id: int
    created_at: datetime

class LabVendorAddressResponse(LabVendorAddressBase):
    id: int
    created_at: datetime 