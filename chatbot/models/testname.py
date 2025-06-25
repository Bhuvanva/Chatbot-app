from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime, Text
from chatbot.models.base import Base

class TestName(Base):
    __tablename__ = 'testname'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True, index=True)
    isDeleted = Column(Boolean, nullable=False)
    createdAt = Column(DateTime(6), nullable=False)
    detailed_description = Column(Text, nullable=True)
    fasting_required = Column(Integer, nullable=True)
    fasting_time = Column(String(10), nullable=True)
    report_time = Column(Integer, nullable=True)
    slot_time_duration = Column(Integer, nullable=True)
    isActive = Column(Boolean, nullable=False) 