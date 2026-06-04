from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from _database import get_db
from _models import User
from _schemas import UserRegister, UserLogin, UserResetPassword, UserResponse
from _auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register")
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone == data.phone).first():
        raise HTTPException(400, "该手机号已注册")
    user = User(
        phone=data.phone,
        password_hash=hash_password(data.password),
        name=data.name or f"用户{data.phone[-4:]}",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.phone)
    return {"token": token, "user": UserResponse.model_validate(user)}


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "手机号或密码错误")
    token = create_access_token(user.phone)
    return {"token": token, "user": UserResponse.model_validate(user)}


@router.post("/reset-password")
def reset_password(data: UserResetPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        raise HTTPException(404, "该手机号未注册")
    user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "密码已重置"}


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user
