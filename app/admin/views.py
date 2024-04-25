from sqladmin import ModelView

from app.user.models import User


class UserAdmin(ModelView, model=User):
    column_list = [c.name for c in User.__table__.c]
    column_details_exclude_list = [User.hashed_password]
    can_delete = False
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"