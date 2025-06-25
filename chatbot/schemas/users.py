from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, EmailStr
from .base import BaseSchema

class UserBase(BaseSchema):
    fullName: Optional[str] = None
    mobileNo: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    isVerified: Optional[int] = 0
    userType: Optional[int] = None
    deviceToken: Optional[str] = None
    updatedAt: Optional[datetime] = None
    last_login: Optional[datetime] = None
    isWalkIn: Optional[bool] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    time_delete: Optional[datetime] = None
    commission_percentage: Optional[int] = None
    is_staff: Optional[bool] = False
    is_superuser: Optional[bool] = False
    createdAt: Optional[datetime] = None
    isLogin: Optional[bool] = False
    deviceType: Optional[int] = None
    age: Optional[str] = None
    gender: Optional[int] = None
    otp: Optional[int] = None
    termcondition: Optional[bool] = False
    updateotp: Optional[int] = None
    profileImage: Optional[str] = None
    socialProviderId: Optional[str] = None
    socialType: Optional[int] = None
    belongsTo: Optional[int] = None
    isFamilyMember: Optional[bool] = False

class UserCreate(UserBase):
    password: str
    email: EmailStr
    mobileNo: str

class UserUpdate(UserBase):
    pass

class UserInDB(UserBase):
    id: int
    createdAt: datetime
    isDeleted: bool
    isActive: bool

class UserResponse(UserBase):
    id: int
    createdAt: datetime
    isDeleted: bool
    isActive: bool 