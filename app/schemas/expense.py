from typing import Optional
from pydantic import BaseModel, Field
from app.core.constants import ExpenseType

class ExpenseCreateSchema(BaseModel):
    type: str = ExpenseType.PURCHASE.value
    name: str = Field(..., min_length=2, max_length=100)
    qty: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=50)
    amount: float = Field(..., gt=0)
    date: str
    notes: Optional[str] = Field(None, max_length=300)

class SettingsSchema(BaseModel):
    accountName: str
    paymentPhone: str
    upiId: str
    customerCarePhone: Optional[str] = "+91 98450 11223"
    deliveryTeamPhone: Optional[str] = "+91 98450 44556"
    pickupAddress: Optional[str] = None
    pickupMapLink: Optional[str] = None
    kitchenLocations: Optional[str] = "[]"
