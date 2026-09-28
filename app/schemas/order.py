from typing import List, Optional
from pydantic import BaseModel, Field
from app.core.constants import OrderStatus, FulfillmentType

class OrderItemSchema(BaseModel):
    itemId: str
    name: str
    bookedKg: float = Field(..., gt=0)
    actualKg: Optional[float] = None
    rate: float = Field(..., ge=0)
    subtotal: float = Field(..., ge=0)
    isMutton: Optional[bool] = False
    isChicken: Optional[bool] = False

class OrderCreateSchema(BaseModel):
    customerName: str = Field(..., min_length=2, max_length=100)
    customerPhone: str = Field(..., min_length=8, max_length=20)
    fulfillmentType: str = FulfillmentType.DELIVERY.value
    kitchenLocation: Optional[str] = None
    deliveryArea: Optional[str] = None
    deliveryAddress: Optional[str] = None
    targetDate: str
    targetTime: str
    orderTakenAt: Optional[str] = None
    items: List[OrderItemSchema] = Field(..., min_items=1)
    specialInstructions: Optional[str] = Field(None, max_length=500)
    totalAmount: float = Field(..., ge=0)
    advancePaid: float = Field(0.0, ge=0)
    discount: float = Field(0.0, ge=0)
    amountPaidAtDispatch: float = Field(0.0, ge=0)
    balanceRemaining: float = Field(0.0, ge=0)
    refundAmount: float = Field(0.0, ge=0)
    cancellationFee: float = Field(0.0, ge=0)
    cancellationReason: Optional[str] = None
    paymentMode: Optional[str] = None
    paymentCollector: Optional[str] = None
    status: str = OrderStatus.BOOKED.value
    isCallback: bool = False

class WeightUpdateSchema(BaseModel):
    actualKg: float = Field(..., gt=0)
    recalculateBill: bool = True

class AuditPaymentSchema(BaseModel):
    discount: float = Field(0.0, ge=0)
    amountPaidNow: float = Field(0.0, ge=0)
    paymentMethod: str = Field(..., max_length=50)
    collectorName: str = Field(..., min_length=2, max_length=100)
    status: str

class OrderCancelSchema(BaseModel):
    refundAmount: float = Field(0.0, ge=0)
    cancellationFee: float = Field(0.0, ge=0)
    cancellationReason: Optional[str] = Field(None, max_length=300)
