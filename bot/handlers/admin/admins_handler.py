from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.base import async_session_factory
from bot.database.repositories import AdminRepository, UserRepository
from bot.keyboards.admin.admins_kb import admins_manage_kb
from bot.states import AdminStates
from bot.config import settings
from bot.utils import logger

router = Router()


@router.callback_query(lambda c: c.data == "admin:admins")
async def admins_panel(callback: CallbackQuery):
    async with async_session_factory() as session:
        repo = AdminRepository(session)
        admins = await repo.get_all_admins()
    await callback.message.edit_text(
        f"🛡 <b>إدارة المشرفين</b>\n\nعدد المشرفين: <b>{len(admins)}</b>",
        reply_markup=admins_manage_kb(admins),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_mgmt:list")
async def list_admins(callback: CallbackQuery):
    async with async_session_factory() as session:
        repo = AdminRepository(session)
        admins = await repo.get_all_admins()
    if not admins:
        await callback.answer("لا يوجد مشرفون حالياً.", show_alert=True)
        return
    lines = [f"🛡 <b>قائمة المشرفين:</b>\n"]
    for a in admins:
        lines.append(f"• <code>{a.telegram_id}</code> — {a.role}")
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=admins_manage_kb(admins),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_mgmt:add")
async def add_admin_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != settings.OWNER_ID:
        await callback.answer("❌ هذه الصلاحية للمالك فقط.", show_alert=True)
        return
    await callback.message.edit_text("➕ أرسل ID المستخدم الذي تريد تعيينه مشرفاً:")
    await state.set_state(AdminStates.waiting_add_admin_id)
    await callback.answer()


@router.message(AdminStates.waiting_add_admin_id)
async def add_admin_execute(message: Message, state: FSMContext):
    if message.from_user.id != settings.OWNER_ID:
        await state.clear()
        return
    if not message.text.strip().isdigit():
        await message.answer("❌ أرسل ID رقمي صحيح.")
        return
    uid = int(message.text.strip())
    await state.clear()
    async with async_session_factory() as session:
        admin_repo = AdminRepository(session)
        user_repo = UserRepository(session)
        await admin_repo.add_admin(uid)
        await user_repo.set_admin(uid, True)
        await session.commit()
    await message.answer(f"✅ تم تعيين <code>{uid}</code> مشرفاً.", parse_mode="HTML")
    logger.info(f"تم إضافة مشرف {uid} بواسطة {message.from_user.id}")


@router.callback_query(lambda c: c.data == "admin_mgmt:remove")
async def remove_admin_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != settings.OWNER_ID:
        await callback.answer("❌ هذه الصلاحية للمالك فقط.", show_alert=True)
        return
    await callback.message.edit_text("➖ أرسل ID المشرف الذي تريد إزالته:")
    await state.set_state(AdminStates.waiting_remove_admin_id)
    await callback.answer()


@router.message(AdminStates.waiting_remove_admin_id)
async def remove_admin_execute(message: Message, state: FSMContext):
    if message.from_user.id != settings.OWNER_ID:
        await state.clear()
        return
    if not message.text.strip().isdigit():
        await message.answer("❌ أرسل ID رقمي صحيح.")
        return
    uid = int(message.text.strip())
    await state.clear()
    async with async_session_factory() as session:
        admin_repo = AdminRepository(session)
        user_repo = UserRepository(session)
        result = await admin_repo.remove_admin(uid)
        await user_repo.set_admin(uid, False)
        await session.commit()
    if result:
        await message.answer(f"✅ تم إزالة المشرف <code>{uid}</code>.", parse_mode="HTML")
    else:
        await message.answer("❌ المشرف غير موجود.")
