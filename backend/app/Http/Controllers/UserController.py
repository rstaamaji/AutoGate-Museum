from sqlalchemy.orm import Session
from app.Services.UserService import UserService
from app.Http.Requests.UserRequest import UserCreateRequest, UserResponse

class UserController:
    @staticmethod
    def index(db: Session):
        service = UserService(db)
        return service.get_all()

    @staticmethod
    def store(user_data: UserCreateRequest, db: Session):
        service = UserService(db)
        return service.create(user_data)
