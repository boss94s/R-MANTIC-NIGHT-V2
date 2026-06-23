from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.base import async_session_factory
from bot.database.repositories import SettingRepository
from bot.keyboards.admin.settings_kb import settings_kb
from bot.states import AdminStates
from bot.utils import logger

router = Router()
SETTING_LABELS = {
    "bot_name": "اسم البوت",
    "welcome": "رسالة الترحيب",
    "free_messages": "عدد الرسائل المجانية",
}


@router.callback_query(lambda c: c.data == "admin:settings")
async def settings_panel(callback: CallbackQuery):
    async with async_session_factory() as session:
        repo = SettingRepository(session)
        maintenance = await repo.get_bool("maintenance_mode")
    await callback.message.edit_text(
        "⚙️ <b>إعدادات البوت</b>\n\nاختر الإعداد الذي تريد تعديله:",
        reply_markup=settings_kb(maintenance),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings:maintenance")
async def toggle_maintenance(callback: CallbackQuery):
    async with async_session_factory() as session:
        repo = SettingRepository(session)
        current = await repo.get_bool("maintenance_mode")
        await repo.set("maintenance_mode", str(not current).lower())
        await session.commit()
    status = "مفعّل" if not current else "معطّل"
    await callback.answer(f"وضع الصيانة: {status}", show_alert=True)
    await settings_panel(callback)


@router.callback_query(F.data.startswith("settings:"))
async def setting_edit_start(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    if key == "maintenance":
        return
    label = SETTING_LABELS.get(key, key)
    await state.update_data(setting_key=key)
    await callback.message.edit_text(f"✏️ أرسل القيمة الجديدة لـ <b>{label}</b>:", parse_mode="HTML")
    await state.set_state(AdminStates.waiting_setting_value)
    await callback.answer()


@router.message(AdminStates.waiting_setting_value)
async def setting_save(message: Message, state: FSMContext):
    data = await state.get_data()
    key = data.get("setting_key")
    await state.clear()
    async with async_session_factory() as session:
        repo = SettingRepository(session)
        await repo.set(key, message.text.strip())
        await session.commit()
    label = SETTING_LABELS.get(key, key)
    await message.answer(f"✅ تم تحديث <b>{label}</b>.", parse_mode="HTML")
    logger.info(f"تم تحديث الإعداد '{key}' بواسطة {message.from_user.id}")
