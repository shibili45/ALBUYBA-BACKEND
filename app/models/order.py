import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.core.constants import OrderStatus, FulfillmentType

class OrderModel(Base):
    __tablename__ = "orders"
    id = Column(String(30), primary_key=True)
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False, index=True)
    fulfillment_type = Column(String(20), default=FulfillmentType.DELIVERY.value)
    kitchen_location = Column(String(100), nullable=True)
    delivery_area = Column(String(120), nullable=True)
    delivery_address = Column(Text, nullable=True)
    target_date = Column(Date, nullable=False, index=True)
    target_time = Column(String(10), nullable=False)
    order_taken_at = Column(String(30), nullable=True)
    special_instructions = Column(Text, nullable=True)
    total_amount = Column(Numeric(10, 2), default=0.0)
    advance_paid = Column(Numeric(10, 2), default=0.0)
    discount = Column(Numeric(10, 2), default=0.0)
    amount_paid_at_dispatch = Column(Numeric(10, 2), default=0.0)
    balance_remaining = Column(Numeric(10, 2), default=0.0)
    refund_amount = Column(Numeric(10, 2), default=0.0)
    cancellation_fee = Column(Numeric(10, 2), default=0.0)
    cancellation_reason = Column(Text, nullable=True)
    payment_mode = Column(String(60), nullable=True)
    payment_collector = Column(String(100), nullable=True)
    status = Column(String(30), default=OrderStatus.BOOKED.value)
    is_callback = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")

class OrderItemModel(Base):
    __tablename__ = "order_items"
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(30), ForeignKey("orders.id"), nullable=False)
    item_id = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    booked_kg = Column(Numeric(6, 3), nullable=False)
    actual_kg = Column(Numeric(6, 3), nullable=True)
    rate = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    is_mutton = Column(Boolean, default=False)
    is_chicken = Column(Boolean, default=False)

    order = relationship("OrderModel", back_populates="items")
