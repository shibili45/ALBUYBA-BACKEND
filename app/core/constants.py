from enum import Enum

class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    ORDERS = "orders"
    KITCHEN = "kitchen"
    DELIVERY = "delivery"

class OrderStatus(str, Enum):
    CALLBACK_REQUIRED = "CALLBACK_REQUIRED"
    BOOKED = "BOOKED"
    IN_KITCHEN = "IN_KITCHEN"
    READY = "READY"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class FulfillmentType(str, Enum):
    DELIVERY = "DELIVERY"
    PICKUP = "PICKUP"
    DINE_IN = "DINE_IN"

class ExpenseType(str, Enum):
    PURCHASE = "PURCHASE"
    SALARY = "SALARY"
    SHOP = "SHOP"

# State machine restrictions
LOCKED_STATUSES = {
    OrderStatus.READY,
    OrderStatus.OUT_FOR_DELIVERY,
    OrderStatus.COMPLETED,
    OrderStatus.CANCELLED
}

CANCELLABLE_STATUSES = {
    OrderStatus.BOOKED,
    OrderStatus.IN_KITCHEN
}

DELETABLE_STATUSES = {
    OrderStatus.BOOKED,
    OrderStatus.IN_KITCHEN,
    OrderStatus.CALLBACK_REQUIRED
}
