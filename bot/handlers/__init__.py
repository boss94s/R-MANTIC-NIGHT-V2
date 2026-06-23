from aiogram import Router
from .admin import admin_router
from .user import user_router


def get_main_router() -> Router:
    main_router = Router()
    main_router.include_router(admin_router)
    main_router.include_router(user_router)
    return main_router
