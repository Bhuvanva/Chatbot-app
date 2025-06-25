from sqlalchemy import Column, BigInteger, String, DateTime, Time, Integer, Numeric, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from chatbot.models.lab_vendor_addresses import LabVendorAddresses  # Ensure model is registered
from chatbot.models.base import Base

class LabVendor(Base):
    __tablename__ = 'lab_vendor'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    lab_owner_email = Column(String(255))
    lab_owner_name = Column(String(255))
    lab_owner_mobile_no = Column(String(255))
    lab_name = Column(String(255))
    lab_email = Column(String(255))
    lab_mobile_no = Column(String(255))
    lab_password = Column(String(255))
    establishment_date = Column(String(255))
    created_at = Column(DateTime(6), nullable=False)
    last_login = Column(DateTime(6), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    # productId_id = Column(BigInteger, ForeignKey('product.id'))
    pathology = Column(Boolean, nullable=False)
    radiology = Column(Boolean, nullable=False)
    isActive = Column(Boolean, nullable=False)
    isDeleted = Column(Boolean, nullable=False)
    isVerified = Column(Boolean, nullable=False)
    alternate_mobile_no = Column(JSON, nullable=False, default=list)
    closing_time = Column(Time(6))
    opening_time = Column(Time(6))
    OneHour = Column(Integer)
    halfHour = Column(Integer)
    lab_homecollection_charge = Column(Numeric(30,2))
    ClosingTimeSession = Column(String(255))
    OpeningTimeSession = Column(String(255))
    addresses = relationship(LabVendorAddresses, back_populates="lab_vendor", cascade="all, delete-orphan")
    lab_types = relationship("LabType", back_populates="lab_vendor", cascade="all, delete-orphan")
    # Removed relationships to non-existent models 