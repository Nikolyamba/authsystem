from typing import Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from server.database.models.user_model import User
from server.database.session import get_db
from server.features import hashed_password

u_router = APIRouter() #u_router как user_router

class UserInfo(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None #если не передано то None
    email: str

class UserRegister(UserInfo):
    password: Annotated[str, Field(min_length=8, max_length=128)]
    repeat_password: Annotated[str, Field(min_length=8, max_length=128)]

@u_router.post('/users', response_model=UserInfo)
async def create_user(data: UserRegister, db: Session = Depends(get_db)):
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
    return new_user


