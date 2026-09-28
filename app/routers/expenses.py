from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.constants import UserRole
from app.core.security import require_roles, get_current_user
from app.models.expense import ExpenseModel, SettingModel
from app.schemas.expense import ExpenseCreateSchema, SettingsSchema

router = APIRouter(prefix="/api", tags=["Expenses & Settings"])

@router.get("/expenses")
def get_expenses(
    date_filter: Optional[str] = Query(None, alias="date"),
    db: Session = Depends(get_db),
    _user = Depends(require_roles([UserRole.SUPERADMIN, UserRole.ADMIN]))
):
    query = db.query(ExpenseModel)
    if date_filter:
        query = query.filter(ExpenseModel.date == date.fromisoformat(date_filter))
    return [{
        "id": e.id, "type": e.type, "name": e.name, "qty": e.qty, "role": e.role,
        "amount": float(e.amount), "date": e.date.isoformat(), "notes": e.notes
    } for e in query.order_by(ExpenseModel.date.desc()).all()]

@router.post("/expenses")
def add_expense(
    payload: ExpenseCreateSchema,
    db: Session = Depends(get_db),
    _user = Depends(require_roles([UserRole.SUPERADMIN, UserRole.ADMIN]))
):
    exp = ExpenseModel(
        type=payload.type, name=payload.name, qty=payload.qty, role=payload.role,
        amount=payload.amount, date=date.fromisoformat(payload.date), notes=payload.notes
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return {"message": "Saved", "id": exp.id}

@router.delete("/expenses/{exp_id}")
def delete_expense(
    exp_id: str,
    db: Session = Depends(get_db),
    _user = Depends(require_roles([UserRole.SUPERADMIN, UserRole.ADMIN]))
):
    db_exp = db.query(ExpenseModel).filter(ExpenseModel.id == exp_id).first()
    if not db_exp:
        raise HTTPException(status_code=404, detail="Expense entry not found")
    db.delete(db_exp)
    db.commit()
    return {"message": "Deleted"}

@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    return {r.key: r.value for r in db.query(SettingModel).all()}

@router.post("/settings")
def save_settings(
    settings: SettingsSchema,
    db: Session = Depends(get_db),
    _user = Depends(require_roles([UserRole.SUPERADMIN, UserRole.ADMIN]))
):
    for k, v in settings.model_dump().items():
        row = db.query(SettingModel).filter(SettingModel.key == k).first()
        if row:
            row.value = str(v)
        else:
            db.add(SettingModel(key=k, value=str(v)))
    db.commit()
    return {"message": "Settings updated"}
