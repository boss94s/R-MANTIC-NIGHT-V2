from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.admin import admin_main_kb
from bot.utils import logger

router = Router()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    await message.answer(
        "🛡 <b>لوحة التحكم</b>\n\nمرحباً بك في لوحة التحكم الإدارية.",
        reply_markup=admin_main_kb(),
        parse_mode="HTML",
    )


@router.callback_query(lambda c: c.data == "admin:main")
async def admin_main_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛡 <b>لوحة التحكم</b>\n\nاختر من القائمة:",
        reply_markup=admin_main_kb(),
        parse_mode="HTML",
    )
    await callback.answer()
