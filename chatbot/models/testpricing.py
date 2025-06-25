from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime, Text, DECIMAL
from chatbot.models.base import Base

class TestPricing(Base):
    __tablename__ = 'testpricing'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(6), nullable=False)
    isDeleted = Column(Boolean, nullable=False)
    test_name_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=True, index=True)
    detailed_description = Column(Text, nullable=True)
    fasting_required = Column(Integer, nullable=True)
    fasting_time = Column(String(10), nullable=True)
    name = Column(String(255), nullable=True)
    report_time = Column(Integer, nullable=True)
    isChange = Column(Boolean, nullable=True)
    isWalkIn = Column(Boolean, nullable=True)
    slot_time_duration = Column(Integer, nullable=True)
    isActive = Column(Boolean, nullable=False)
    labbuddy_share = Column(Integer, nullable=True)
    vendor_discount = Column(Integer, nullable=True)
    vendor_labbuddy_rate = Column(Integer, nullable=True)
    vendor_price = Column(Integer, nullable=True)
    lb_app_price = Column(Integer, nullable=True)
    lb_user_discount = Column(Integer, nullable=True)
    price = Column(Integer, nullable=True)
    special_discount = Column(Integer, nullable=True) 