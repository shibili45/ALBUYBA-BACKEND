import uuid
from sqlalchemy import Column, String, Numeric, Boolean, Text
from app.db.session import Base

class MenuItemModel(Base):
    __tablename__ = "menu_items"
    id = Column(String(50), primary_key=True, default=lambda: f"item_{uuid.uuid4().hex[:8]}")
    name = Column(String(100), nullable=False)
    rate = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(20), default="KG")
    category = Column(String(50), default="Mandi")
    is_mutton = Column(Boolean, default=False)
    is_chicken = Column(Boolean, default=False)
    note = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
