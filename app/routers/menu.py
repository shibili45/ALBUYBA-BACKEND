from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.constants import UserRole
from app.core.security import require_roles, get_current_user
from app.models.menu import MenuItemModel
from app.schemas.menu import MenuItemCreateSchema

router = APIRouter(prefix="/api/menu", tags=["Menu"])

@router.get("")
def get_menu(db: Session = Depends(get_db)):
    items = db.query(MenuItemModel).all()
    return [{
        "id": i.id,
        "name": i.name,
        "rate": float(i.rate),
        "unit": i.unit,
        "category": i.category,
        "isMutton": i.is_mutton,
        "isChicken": i.is_chicken,
        "note": i.note,
        "active": i.active
    } for i in items]

@router.post("")
def add_item(
    item: MenuItemCreateSchema,
    db: Session = Depends(get_db),
    _user = Depends(require_roles([UserRole.SUPERADMIN, UserRole.ADMIN]))
):
    new_item = MenuItemModel(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"message": "Created", "id": new_item.id}

@router.put("/{item_id}")
def update_item(
    item_id: str,
    item: MenuItemCreateSchema,
    db: Session = Depends(get_db),
    _user = Depends(require_roles([UserRole.SUPERADMIN, UserRole.ADMIN]))
):
    db_item = db.query(MenuItemModel).filter(MenuItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    return {"message": "Updated"}

@router.delete("/{item_id}")
def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    _user = Depends(require_roles([UserRole.SUPERADMIN, UserRole.ADMIN]))
):
    db_item = db.query(MenuItemModel).filter(MenuItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Deleted"}
