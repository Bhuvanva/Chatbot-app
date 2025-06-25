from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from chatbot.models.base import Base

class LabVendorAddresses(Base):
    __tablename__ = 'lab_vendor_addresses'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    address = Column(String(255))
    city = Column(String(255))
    state = Column(String(255))
    country = Column(String(255))
    pincode = Column(String(255))
    created_at = Column(DateTime(6), nullable=False)
    lab_vendor_id = Column(BigInteger, ForeignKey('lab_vendor.id'), nullable=False)
    lab_vendor = relationship("LabVendor", back_populates="addresses") 