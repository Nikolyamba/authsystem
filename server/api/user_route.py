from typing import Optional, Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session

from server.api.jwt_auth import create_access_token, create_refresh_token
from server.database.models.user_model import User
from server.database.session import get_db
from server.features import hashed_password

u_router = APIRouter() #u_router как user_router

class UserInfo(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None #если не передано то None
    email: EmailStr

class UserRegister(UserInfo):
    password: Annotated[str, Field(min_length=8, max_length=128)]
    repeat_password: Annotated[str, Field(min_length=8, max_length=128)]

@u_router.post('/users')
async def create_user(data: UserRegister, db: Session = Depends(get_db)) -> dict:
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail='Такой email уже используется!')
    if data.password != data.repeat_password:
        raise HTTPException(status_code=400, detail='Указанные пароли не совпадают!')
    new_user = User(name = data.name,
                    surname = data.surname,
                    patronymic = data.patronymic,
                    email = data.email,
                    password = hashed_password(data.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token(user_id=new_user.id)
    refresh_token = create_refresh_token(user_id=new_user.id)
    return {"success": True, "payload": {"access_token": access_token, "refresh_token": refresh_token}}

class UserLogin(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=128)]

@u_router.post('/login')
async def login(data: UserLogin, db: Session = Depends(get_db)) -> dict:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not bcrypt.checkpw(data.password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="email или пароль введены неправильно")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="пользователь удалён")
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return {"success": True, "payload": {"access_token": access_token, "refresh_token": refresh_token}}
