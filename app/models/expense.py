import uuid
from sqlalchemy import Column, String, Numeric, Date, Text
from app.db.session import Base
from app.core.constants import ExpenseType

class ExpenseModel(Base):
    __tablename__ = "expenses"
    id = Column(String(50), primary_key=True, default=lambda: f"exp-{uuid.uuid4().hex[:8]}")
    type = Column(String(20), default=ExpenseType.PURCHASE.value, nullable=False)
    name = Column(String(100), nullable=False)
    qty = Column(String(50), nullable=True)
    role = Column(String(50), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)

class SettingModel(Base):
    __tablename__ = "settings"
    key = Column(String(50), primary_key=True)
    value = Column(Text, nullable=False)
