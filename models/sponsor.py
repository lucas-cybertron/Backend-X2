# models/sponsor.py
from sqlalchemy import Column, Integer, String, Text
from core.database import Base

class Sponsor(Base):
    __tablename__ = "sponsors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    logo_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    website = Column(String, nullable=True)
