from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.base import async_session_factory
from bot.database.repositories import UserRepository
from bot.keyboards.admin.users_kb import users_manage_kb, user_detail_kb
from bot.states import AdminStates
from bot.utils import logger
from bot.utils.helpers import format_user_info

router = Router()


@router.callback_query(lambda c: c.data == "admin:users")
async def users_panel(callback: CallbackQuery):
    async with async_session_factory() as session:
        repo = UserRepository(session)
        count = await repo.count()
    text = f"👥 <b>إدارة المستخدمين</b>\n\nإجمالي المستخدمين: <b>{count}</b>"
    await callback.message.edit_text(text, reply_markup=users_manage_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data == "user:search")
async def search_user_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔍 أرسل معرّف المستخدم (ID) أو اسم المستخدم (@username):"
    )
    await state.set_state(AdminStates.waiting_search_user)
    await callback.answer()


@router.message(AdminStates.waiting_search_user)
async def search_user_result(message: Message, state: FSMContext):
    query = message.text.strip().lstrip("@")
    async with async_session_factory() as session:
        repo = UserRepository(session)
        if query.isdigit():
            user = await repo.get_by_telegram_id(int(query))
            users = [user] if user else []
        else:
            users = await repo.search_users(query)

    await state.clear()
    if not users:
        await message.answer("❌ لم يُعثر على مستخدم.")
        return

    for user in users[:5]:
        ban_status = "🚫 محظور" if user.is_banned else "✅ نشط"
        text = (
            f"👤 <b>معلومات المستخدم</b>\n\n"
            f"🆔 ID: <code>{user.telegram_id}</code>\n"
            f"📛 الاسم: {user.first_name}\n"
            f"🔖 المعرف: @{user.username or 'لا يوجد'}\n"
            f"📊 الحالة: {ban_status}\n"
            f"💬 الرسائل: {user.total_messages}\n"
            f"📅 تاريخ التسجيل: {user.created_at.strftime('%Y-%m-%d')}"
        )
        await message.answer(text, reply_markup=user_detail_kb(user), parse_mode="HTML")


@router.callback_query(lambda c: c.data == "user:ban")
async def ban_user_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🚫 أرسل ID المستخدم الذي تريد حظره:")
    await state.set_state(AdminStates.waiting_ban_user_id)
    await callback.answer()


@router.message(AdminStates.waiting_ban_user_id)
async def ban_user_execute(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("❌ أرسل ID رقمي صحيح.")
        return
    uid = int(message.text.strip())
    await state.clear()
    async with async_session_factory() as session:
        repo = UserRepository(session)
        result = await repo.set_banned(uid, True)
        await session.commit()
    if result:
        await message.answer(f"✅ تم حظر المستخدم <code>{uid}</code>.", parse_mode="HTML")
        logger.info(f"تم حظر المستخدم {uid} بواسطة {message.from_user.id}")
    else:
        await message.answer("❌ المستخدم غير موجود.")


@router.callback_query(F.data.startswith("user:ban:"))
async def ban_user_from_detail(callback: CallbackQuery):
    uid = int(callback.data.split(":")[2])
    async with async_session_factory() as session:
        repo = UserRepository(session)
        await repo.set_banned(uid, True)
        await session.commit()
    await callback.message.edit_text(f"✅ تم حظر المستخدم <code>{uid}</code>.", parse_mode="HTML")
    await callback.answer("تم الحظر ✅")


@router.callback_query(lambda c: c.data == "user:unban")
async def unban_user_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✅ أرسل ID المستخدم الذي تريد فك حظره:")
    await state.set_state(AdminStates.waiting_unban_user_id)
    await callback.answer()


@router.message(AdminStates.waiting_unban_user_id)
async def unban_user_execute(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("❌ أرسل ID رقمي صحيح.")
        return
    uid = int(message.text.strip())
    await state.clear()
    async with async_session_factory() as session:
        repo = UserRepository(session)
        result = await repo.set_banned(uid, False)
        await session.commit()
    if result:
        await message.answer(f"✅ تم فك حظر المستخدم <code>{uid}</code>.", parse_mode="HTML")
    else:
        await message.answer("❌ المستخدم غير موجود.")


@router.callback_query(F.data.startswith("user:unban:"))
async def unban_user_from_detail(callback: CallbackQuery):
    uid = int(callback.data.split(":")[2])
    async with async_session_factory() as session:
        repo = UserRepository(session)
        await repo.set_banned(uid, False)
        await session.commit()
    await callback.message.edit_text(f"✅ تم فك حظر المستخدم <code>{uid}</code>.", parse_mode="HTML")
    await callback.answer("تم فك الحظر ✅")
