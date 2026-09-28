from typing import Optional
from pydantic import BaseModel, Field

class MenuItemCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    rate: float = Field(..., ge=0)
    unit: str = Field("KG", max_length=20)
    category: str = Field("Mandi", max_length=50)
    is_mutton: bool = False
    is_chicken: bool = False
    note: Optional[str] = Field(None, max_length=500)
    active: bool = True

class MenuItemResponseSchema(MenuItemCreateSchema):
    id: str
