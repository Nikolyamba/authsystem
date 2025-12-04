from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

u_router = APIRouter() #u_router как user_router

class UserRegister(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None #если не передано то None
