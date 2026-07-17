from sqlalchemy.orm import Session
from app.Models.User import User
from app.Http.Requests.UserRequest import UserCreateRequest

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(User).all()

    def create(self, user_data: UserCreateRequest):
        new_user = User(name=user_data.name, email=user_data.email)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user
