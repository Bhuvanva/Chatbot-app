from datetime import datetime
from typing import Optional, List
from .base import BaseSchema
from pydantic import BaseModel, Field

class LabVendorBase(BaseSchema):
    lab_owner_email: Optional[str] = None
    lab_owner_name: Optional[str] = None
    lab_name: Optional[str] = None
    last_login: Optional[datetime] = None
    isVerified: Optional[bool] = None
    isDeleted: Optional[bool] = None
    isActive: Optional[bool] = None

class LabVendorCreate(LabVendorBase):
    lab_owner_email: str
    lab_owner_name: str
    lab_name: str

class LabVendorUpdate(LabVendorBase):
    pass

class LabVendorInDB(LabVendorBase):
    id: int
    created_at: datetime
    isDeleted: bool
    isActive: bool

class LabVendorResponse(LabVendorBase):
    id: int
    created_at: datetime
    isDeleted: bool
    isActive: bool

class ServicesModel(BaseModel):
    pathology: bool = False
    radiology: bool = False

class NearbyLabResponse(BaseModel):
    id: int
    lab_name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: str
    distance: Optional[float] = Field(None, description="Distance in kilometers")
    services: ServicesModel
    home_collection_charge: float = Field(default=0.0, description="Home collection charge in INR")
    test_name: Optional[str] = Field(None, description="Name of the test if filtered by test name")

    class Config:
        from_attributes = True 