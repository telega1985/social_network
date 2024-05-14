from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin

from app.activity.router import router_activity
from app.admin.auth import authentication_backend
from app.admin.views import UserAdmin
from app.database import engine
from app.post.router import router_post
from app.profile.router import router_profile
from app.user.router import router_auth, router_user

app = FastAPI(title="SocialNet")


app.include_router(router_auth)
app.include_router(router_user)
app.include_router(router_post)
app.include_router(router_activity)
app.include_router(router_profile)

# Админка

admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UserAdmin)

# Путь к папке static (frontend)

app.mount("/static", StaticFiles(directory="app/static"), "static")
