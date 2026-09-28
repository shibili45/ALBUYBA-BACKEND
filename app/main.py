import logging
import json
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.config import settings
from app.core.constants import UserRole
from app.core.security import get_password_hash
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.models.user import UserModel
from app.models.menu import MenuItemModel
from app.models.expense import SettingModel
from app.routers import auth, orders, menu, expenses

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("opsdesk")

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Secure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global Error Handlers (Prevents leaking SQL/database traces)
@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    logger.error(f"Database Integrity Violation on {request.method} {request.url.path}: {exc}")
    orig_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
    
    if "unique constraint" in orig_msg.lower() or "duplicate key" in orig_msg.lower():
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "A record with this identifier or unique value already exists. Please refresh and retry."}
        )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Data constraint violation. Please verify related records."}
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"SQLAlchemy Database Error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A secure database error occurred. The technical trace has been logged."}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Request Validation Failure on {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Submitted payload failed validation constraints.", "errors": exc.errors()}
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Unhandled Exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected operational error occurred on the server."}
    )

# Routers
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(menu.router)
app.include_router(expenses.router)

def seed_defaults():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(UserModel).count() == 0:
            defaults = [
                ("superadmin", "123", "Master Admin", UserRole.SUPERADMIN.value),
                ("admin", "123", "Operations Lead", UserRole.ADMIN.value),
                ("orders", "123", "Zaid (Call Desk)", UserRole.ORDERS.value),
                ("kitchen", "123", "Ustad Bilal (Kitchen)", UserRole.KITCHEN.value),
                ("delivery", "123", "Rider Team", UserRole.DELIVERY.value),
            ]
            for u, p, name, role in defaults:
                db.add(UserModel(
                    id=f"u_{u}",
                    username=u,
                    password_hash=get_password_hash(p),
                    name=name,
                    role=role
                ))
            db.commit()

        if db.query(MenuItemModel).count() == 0:
            db.add_all([
                MenuItemModel(id="item_mutton", name="Mutton Mandi", rate=1800, unit="KG", category="Mandi", is_mutton=True, note="Includes 1.000 kg meat + 1.000 kg rice (Serves 4-5)"),
                MenuItemModel(id="item_chicken", name="Chicken Mandi", rate=700, unit="Full", category="Mandi", is_chicken=True, note="Includes 1 full chicken + 1.000 kg rice (Serves 4-5)"),
                MenuItemModel(id="item_rice", name="Mandi Rice Only", rate=200, unit="KG", category="Rice", note="Smoked authentic long-grain mandi rice (Serves 5-6)"),
                MenuItemModel(id="item_madfoon", name="Chicken Madfoon", rate=500, unit="Half", category="Madfoon", is_chicken=True, note="Half chicken slow foil-roasted with mandi spices"),
            ])
            db.commit()

        initial_kitchens = [
            {
                "id": "loc_comm",
                "name": "Commercial Street Central Kitchen",
                "address": "Shop #12, Grand Sultan Complex, Commercial Street, Bengaluru",
                "mapLink": "https://maps.google.com/?q=Commercial+Street+Bengaluru"
            },
            {
                "id": "loc_indira",
                "name": "Indiranagar Cloud Kitchen",
                "address": "100ft Road, Near Toit, Indiranagar, Bengaluru",
                "mapLink": "https://maps.google.com/?q=Indiranagar+100ft+Road+Bengaluru"
            }
        ]

        default_settings = {
            "accountName": "ALBUYBA AUTHENTIC MANDI",
            "paymentPhone": "+91 98450 88990",
            "upiId": "mandiorders@okaxis",
            "customerCarePhone": "+91 98450 11223",
            "deliveryTeamPhone": "+91 98450 44556",
            "pickupAddress": "Shop #12, Grand Sultan Complex, Commercial Street, Bengaluru",
            "pickupMapLink": "https://maps.google.com/?q=Commercial+Street+Bengaluru",
            "kitchenLocations": json.dumps(initial_kitchens)
        }

        for k, v in default_settings.items():
            if not db.query(SettingModel).filter(SettingModel.key == k).first():
                db.add(SettingModel(key=k, value=str(v)))
        db.commit()
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    seed_defaults()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
