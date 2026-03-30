from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON
from database import Base
from datetime import datetime
import uuid

class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    address = Column(Text, default="")
    city = Column(String, default="")
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    website = Column(String, nullable=True)
    has_website = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    types = Column(Text, default="")
    source = Column(String, default="")
    merged_sources = Column(Text, default="")
    score = Column(Integer, default=5)
    priority = Column(String, default="medium")
    reason = Column(Text, default="")
    pain_points = Column(JSON, default=list)
    suggested_opening = Column(Text, default="")
    tech_hints = Column(Text, default="")
    social_media = Column(Text, default="")
    website_live = Column(Boolean, default=False)
    has_contact_form = Column(Boolean, default=False)
    lat = Column(Float, default=0.0)
    lon = Column(Float, default=0.0)
    session_id = Column(String, index=True)
    status = Column(String, default="NEW") # NEW, READY, EMAILED, ENRICHMENTFAILED, UNENRICHABLE
    enrich_attempts = Column(Integer, default=0)
    email_quality_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
