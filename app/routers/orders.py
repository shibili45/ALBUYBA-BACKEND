import re
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.constants import UserRole, OrderStatus, LOCKED_STATUSES, CANCELLABLE_STATUSES, DELETABLE_STATUSES
from app.core.security import require_roles, get_current_user
from app.models.order import OrderModel, OrderItemModel
from app.schemas.order import OrderCreateSchema, WeightUpdateSchema, AuditPaymentSchema, OrderCancelSchema

router = APIRouter(prefix="/api/orders", tags=["Orders"])

def get_next_order_id(db: Session, is_callback: bool) -> str:
    prefix = "CB" if is_callback else "ORD"
    orders = db.query(OrderModel.id).filter(OrderModel.id.like(f"{prefix}-%")).all()
    max_num = 100
    for (oid,) in orders:
        match = re.match(rf"^{prefix}-(\d+)$", oid)
        if match:
            max_num = max(max_num, int(match.group(1)))
    next_num = max_num + 1
    new_id = f"{prefix}-{next_num}"
    while db.query(OrderModel.id).filter(OrderModel.id == new_id).first():
        next_num += 1
        new_id = f"{prefix}-{next_num}"
    return new_id

def serialize_order(o: OrderModel):
    return {
        "id": o.id,
        "customerName": o.customer_name,
        "customerPhone": o.customer_phone,
        "fulfillmentType": o.fulfillment_type,
        "kitchenLocation": o.kitchen_location,
        "deliveryArea": o.delivery_area,
        "deliveryAddress": o.delivery_address,
        "targetDate": o.target_date.isoformat(),
        "targetTime": o.target_time,
        "orderTakenAt": o.order_taken_at,
        "specialInstructions": o.special_instructions,
        "totalAmount": float(o.total_amount),
        "advancePaid": float(o.advance_paid),
        "discount": float(o.discount),
        "amountPaidAtDispatch": float(o.amount_paid_at_dispatch),
        "balanceRemaining": float(o.balance_remaining),
        "refundAmount": float(o.refund_amount or 0.0),
        "cancellationFee": float(o.cancellation_fee or 0.0),
        "cancellationReason": o.cancellation_reason,
        "paymentMode": o.payment_mode,
        "paymentCollector": o.payment_collector,
        "status": o.status,
        "isCallback": o.is_callback,
        "createdAt": o.created_at.strftime("%Y-%m-%d"),
        "items": [{
            "itemId": item.item_id,
            "name": item.name,
            "bookedKg": float(item.booked_kg),
            "actualKg": float(item.actual_kg) if item.actual_kg is not None else None,
            "rate": float(item.rate),
            "subtotal": float(item.subtotal),
            "isMutton": item.is_mutton,
            "isChicken": item.is_chicken
        } for item in o.items]
    }

@router.get("")
def get_orders(
    date_filter: Optional[str] = Query(None, alias="date"),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _user = Depends(get_current_user)
):
    query = db.query(OrderModel)
    if date_filter:
        query = query.filter(OrderModel.target_date == date.fromisoformat(date_filter))
    if from_date and to_date:
        query = query.filter(OrderModel.target_date.between(date.fromisoformat(from_date), date.fromisoformat(to_date)))
    if status_filter and status_filter != "ALL":
        query = query.filter(OrderModel.status == status_filter)
        
    orders = query.order_by(OrderModel.target_date.desc(), OrderModel.target_time.asc()).all()
    return [serialize_order(o) for o in orders]

@router.post("")
def create_order(
    payload: OrderCreateSchema,
    db: Session = Depends(get_db),
    _user = Depends(require_roles([UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.ORDERS]))
):
    order_id = get_next_order_id(db, payload.isCallback)
    
    order = OrderModel(
        id=order_id,
        customer_name=payload.customerName,
        customer_phone=payload.customerPhone,
        fulfillment_type=payload.fulfillmentType,
        kitchen_location=payload.kitchenLocation,
        delivery_area=payload.deliveryArea,
        delivery_address=payload.deliveryAddress,
        target_date=date.fromisoformat(payload.targetDate),
        target_time=payload.targetTime,
        order_taken_at=payload.orderTakenAt,
        special_instructions=payload.specialInstructions,
        total_amount=payload.totalAmount,
        advance_paid=payload.advancePaid,
        discount=payload.discount,
        amount_paid_at_dispatch=payload.amountPaidAtDispatch,
        balance_remaining=payload.balanceRemaining,
        refund_amount=payload.refundAmount,
        cancellation_fee=payload.cancellationFee,
        cancellation_reason=payload.cancellationReason,
        payment_mode=payload.paymentMode,
        payment_collector=payload.paymentCollector or "Order Desk",
        status=OrderStatus.CALLBACK_REQUIRED.value if payload.isCallback else payload.status,
        is_callback=payload.isCallback
    )
    db.add(order)
    
    for item in payload.items:
        db.add(OrderItemModel(
            order_id=order_id,
            item_id=item.itemId,
            name=item.name,
            booked_kg=item.bookedKg,
            actual_kg=item.actualKg,
            rate=item.rate,
            subtotal=item.subtotal,
            is_mutton=item.isMutton,
            is_chicken=item.isChicken
        ))
        
    db.commit()
    db.refresh(order)
    return serialize_order(order)

@router.put("/{order_id}")
def update_order(
    order_id: str,
    payload: OrderCreateSchema,
    db: Session = Depends(get_db),
    _user = Depends(require_roles([UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.ORDERS]))
):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order #{order_id} not found.")
        
    if order.status in [s.value for s in LOCKED_STATUSES]:
        raise HTTPException(
            status_code=400,
            detail=f"Order #{order_id} is in status '{order.status}' and is locked against modifications."
        )

    order.customer_name = payload.customerName
    order.customer_phone = payload.customerPhone
    order.fulfillment_type = payload.fulfillmentType
    order.kitchen_location = payload.kitchenLocation
    order.delivery_area = payload.deliveryArea
    order.delivery_address = payload.deliveryAddress
    order.target_date = date.fromisoformat(payload.targetDate)
    order.target_time = payload.targetTime
    if payload.orderTakenAt:
        order.order_taken_at = payload.orderTakenAt
    order.special_instructions = payload.specialInstructions
    order.total_amount = payload.totalAmount
    order.advance_paid = payload.advancePaid
    order.balance_remaining = payload.balanceRemaining
    order.is_callback = payload.isCallback
    order.status = payload.status

    db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).delete()
    for item in payload.items:
        db.add(OrderItemModel(
            order_id=order_id,
            item_id=item.itemId,
            name=item.name,
            booked_kg=item.bookedKg,
            actual_kg=item.actualKg,
            rate=item.rate,
            subtotal=item.subtotal,
            is_mutton=item.isMutton,
            is_chicken=item.isChicken
        ))
    db.commit()
    return serialize_order(order)

@router.patch("/{order_id}/cancel")
def cancel_order_with_settlement(
    order_id: str,
    payload: OrderCancelSchema,
    db: Session = Depends(get_db),
    _user = Depends(require_roles([UserRole.SUPERADMIN, UserRole.ADMIN]))
):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order #{order_id} not found.")

    if order.status not in [s.value for s in CANCELLABLE_STATUSES]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel order #{order_id} in status '{order.status}'. Cancellation is only allowed before packing."
        )

    order.status = OrderStatus.CANCELLED.value
    order.refund_amount = payload.refundAmount
    order.cancellation_fee = payload.cancellationFee
    order.cancellation_reason = payload.cancellationReason
    order.balance_remaining = 0.0
    order.is_callback = False
    
    db.commit()
    db.refresh(order)
    return serialize_order(order)

@router.patch("/{order_id}/status")
def patch_status(
    order_id: str,
    status: str = Query(...),
    db: Session = Depends(get_db),
    _user = Depends(get_current_user)
):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order #{order_id} not found.")
    
    # Enforce role-based state progressions
    role = str(_user.role).lower()
    if role == "kitchen" and status not in ["IN_KITCHEN", "READY"]:
        raise HTTPException(status_code=403, detail="Kitchen staff can only transition orders to IN_KITCHEN or READY.")
    if role == "delivery" and status not in ["OUT_FOR_DELIVERY", "COMPLETED"]:
        raise HTTPException(status_code=403, detail="Delivery team can only transition orders to OUT_FOR_DELIVERY or COMPLETED.")

    if status == OrderStatus.CANCELLED.value and order.status not in [s.value for s in CANCELLABLE_STATUSES]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel order #{order_id} in status '{order.status}'."
        )

    order.status = status
    if status == OrderStatus.COMPLETED.value:
        order.amount_paid_at_dispatch = float(order.amount_paid_at_dispatch) + float(order.balance_remaining)
        order.balance_remaining = 0.0
    elif status == OrderStatus.CANCELLED.value:
        order.balance_remaining = 0.0
        
    if status != OrderStatus.CALLBACK_REQUIRED.value:
        order.is_callback = False
        
    db.commit()
    return {"message": "Status updated", "status": order.status}

@router.delete("/{order_id}")
def delete_order(
    order_id: str,
    db: Session = Depends(get_db),
    _user = Depends(require_roles([UserRole.SUPERADMIN, UserRole.ADMIN]))
):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order #{order_id} not found.")
        
    if order.status not in [s.value for s in DELETABLE_STATUSES]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete order #{order_id} in status '{order.status}'."
        )
        
    db.delete(order)
    db.commit()
    return {"message": f"Order #{order_id} deleted successfully."}

@router.patch("/{order_id}/weight")
def adjust_weight(
    order_id: str,
    weight: WeightUpdateSchema,
    db: Session = Depends(get_db),
    _user = Depends(require_roles([UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.KITCHEN]))
):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order #{order_id} not found.")
        
    mutton_item = db.query(OrderItemModel).filter(
        OrderItemModel.order_id == order_id,
        OrderItemModel.is_mutton == True
    ).first()
    
    if not mutton_item:
        raise HTTPException(status_code=400, detail="This order does not contain a mutton butcher item.")
        
    mutton_item.actual_kg = weight.actualKg
    if weight.recalculateBill:
        mutton_item.subtotal = round(float(weight.actualKg) * float(mutton_item.rate), 2)
        all_items = db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).all()
        new_total = sum(float(i.subtotal) for i in all_items)
        order.total_amount = new_total
        order.balance_remaining = max(0.0, new_total - float(order.advance_paid) - float(order.discount))
        
    db.commit()
    return serialize_order(order)

@router.patch("/{order_id}/audit")
def dispatch_audit(
    order_id: str,
    audit: AuditPaymentSchema,
    db: Session = Depends(get_db),
    _user = Depends(require_roles([UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.DELIVERY]))
):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order #{order_id} not found.")
        
    order.discount = audit.discount
    order.amount_paid_at_dispatch = audit.amountPaidNow
    order.payment_mode = audit.paymentMethod
    order.payment_collector = audit.collectorName
    order.status = audit.status
    net_bill = max(0.0, float(order.total_amount) - float(audit.discount))
    order.balance_remaining = max(0.0, net_bill - float(order.advance_paid) - float(audit.amountPaidNow))
    
    db.commit()
    return serialize_order(order)
