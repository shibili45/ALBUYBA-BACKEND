from pydantic import BaseModel, Field
from app.core.constants import UserRole

class UserLoginSchema(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)

class UserCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=100)
    role: str = UserRole.ORDERS.value

class UserResponseSchema(BaseModel):
    id: str
    username: str
    name: str
    role: str
