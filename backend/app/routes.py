from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.Http.Controllers.UserController import UserController
from app.Http.Requests.UserRequest import UserCreateRequest, UserResponse

api_router = APIRouter()

@api_router.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return UserController.index(db)

@api_router.post("/users", response_model=UserResponse)
def create_user(user_data: UserCreateRequest, db: Session = Depends(get_db)):
    return UserController.store(user_data, db)
