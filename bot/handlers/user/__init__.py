from aiogram import Router
from .start_handler import router as start_router
from .chat_handler import router as chat_router
from .characters_handler import router as chars_router
from .conversations_handler import router as conv_router

user_router = Router()
user_router.include_router(start_router)
user_router.include_router(chars_router)
user_router.include_router(conv_router)
user_router.include_router(chat_router)
