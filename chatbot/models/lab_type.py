from sqlalchemy import Column, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.lab_vendor import LabVendor

class LabType(Base):
    __tablename__ = 'lab_type'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)  # To store 'national' or 'local'
    lab_id = Column(BigInteger, ForeignKey('lab_vendor.id'), nullable=False)
    
    # Complete the bidirectional relationship
    lab_vendor = relationship("LabVendor", back_populates="lab_types") 
    