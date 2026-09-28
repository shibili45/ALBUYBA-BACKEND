import uuid
from sqlalchemy import Column, String
from app.db.session import Base
from app.core.constants import UserRole

class UserModel(Base):
    __tablename__ = "users"
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(20), default=UserRole.ORDERS.value, nullable=False)
