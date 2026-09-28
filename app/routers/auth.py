from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.constants import UserRole
from app.core.security import verify_password, get_password_hash, create_access_token, require_roles
from app.models.user import UserModel
from app.schemas.user import UserLoginSchema, UserCreateSchema, UserResponseSchema

router = APIRouter(prefix="/api", tags=["Auth & Users"])

@router.post("/auth/login")
def login(creds: UserLoginSchema, db: Session = Depends(get_db)):
    clean_username = creds.username.strip().lower()
    user = db.query(UserModel).filter(UserModel.username == clean_username).first()
    
    if not user or not verify_password(creds.password.strip(), user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    token = create_access_token(data={
        "sub": user.id,
        "username": user.username,
        "name": user.name,
        "role": user.role
    })
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "role": user.role,
            "token": token
        },
        "token": token
    }

@router.get("/users", response_model=list[UserResponseSchema])
def list_users(
    db: Session = Depends(get_db),
    _user = Depends(require_roles([UserRole.SUPERADMIN]))
):
    return db.query(UserModel).all()

@router.post("/users", response_model=UserResponseSchema)
def create_user(
    payload: UserCreateSchema,
    db: Session = Depends(get_db),
    _user = Depends(require_roles([UserRole.SUPERADMIN]))
):
    clean_username = payload.username.strip().lower()
    if db.query(UserModel).filter(UserModel.username == clean_username).first():
        raise HTTPException(status_code=409, detail="A user with this username already exists.")
        
    new_user = UserModel(
        username=clean_username,
        password_hash=get_password_hash(payload.password.strip()),
        name=payload.name.strip(),
        role=payload.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
