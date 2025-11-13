# schemas/sponsor.py
from pydantic import BaseModel, HttpUrl
from typing import Optional

class SponsorBase(BaseModel):
    name: str
    logo_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    website: Optional[HttpUrl] = None

class SponsorCreate(SponsorBase):
    pass

class SponsorUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    website: Optional[HttpUrl] = None

class SponsorResponse(SponsorBase):
    id: int

    class Config:
        orm_mode = True
