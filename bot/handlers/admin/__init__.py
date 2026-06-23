from aiogram import Router
from bot.filters import IsAdmin
from .main_handler import router as main_router
from .statistics_handler import router as stats_router
from .users_handler import router as users_router
from .admins_handler import router as admins_router
from .characters_handler import router as chars_router
from .broadcast_handler import router as broadcast_router
from .channels_handler import router as channels_router
from .settings_handler import router as settings_router
from .backup_handler import router as backup_router

admin_router = Router()
admin_router.message.filter(IsAdmin())
admin_router.callback_query.filter(IsAdmin())

admin_router.include_router(main_router)
admin_router.include_router(stats_router)
admin_router.include_router(users_router)
admin_router.include_router(admins_router)
admin_router.include_router(chars_router)
admin_router.include_router(broadcast_router)
admin_router.include_router(channels_router)
admin_router.include_router(settings_router)
admin_router.include_router(backup_router)
