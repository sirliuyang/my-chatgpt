# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
from src.crud.crud_user import user_crud
from src.services.user_service import UserService

user_service = UserService(user_crud)