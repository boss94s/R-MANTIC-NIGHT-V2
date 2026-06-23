from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.base import async_session_factory
from bot.database.repositories import UserRepository, AdminRepository
from bot.keyboards.admin.broadcast_kb import broadcast_target_kb, broadcast_confirm_kb
from bot.services.broadcast_service import BroadcastService
from bot.states import AdminStates
from bot.utils import logger

router = Router()


@router.callback_query(lambda c: c.data == "admin:broadcast")
async def broadcast_panel(callback: CallbackQuery):
    await callback.message.edit_text(
        "📢 <b>الإذاعة</b>\n\nاختر الجمهور المستهدف:",
        reply_markup=broadcast_target_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("broadcast:"))
async def broadcast_target(callback: CallbackQuery, state: FSMContext):
    target = callback.data.split(":")[1]
    if target in ("all", "admins"):
        await state.update_data(broadcast_target=target)
        await callback.message.edit_text(
            "📝 أرسل الرسالة التي تريد بثّها:\n\n"
            "<i>يمكنك إرسال نص أو صورة أو أي محتوى آخر.</i>",
            parse_mode="HTML",
        )
        await state.set_state(AdminStates.waiting_broadcast_message)
        await callback.answer()
    elif target == "confirm":
        await send_broadcast(callback, state)


@router.message(AdminStates.waiting_broadcast_message)
async def receive_broadcast_message(message: Message, state: FSMContext):
    await state.update_data(
        broadcast_message_id=message.message_id,
        broadcast_from_chat=message.chat.id,
    )
    data = await state.get_data()
    target = data.get("broadcast_target", "all")
    target_ar = "جميع المستخدمين" if target == "all" else "المشرفون فقط"

    await message.answer(
        f"📢 <b>تأكيد الإذاعة</b>\n\n"
        f"الجمهور: <b>{target_ar}</b>\n\n"
        f"هل تريد إرسال هذه الرسالة؟",
        reply_markup=broadcast_confirm_kb(),
        parse_mode="HTML",
    )


@router.callback_query(lambda c: c.data == "broadcast:confirm")
async def send_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot = None):
    data = await state.get_data()
    await state.clear()
    target = data.get("broadcast_target", "all")
    msg_id = data.get("broadcast_message_id")
    from_chat = data.get("broadcast_from_chat")

    async with async_session_factory() as session:
        if target == "admins":
            repo = AdminRepository(session)
            user_ids = await repo.get_all_admin_ids()
        else:
            repo = UserRepository(session)
            user_ids = await repo.get_all_ids()

    await callback.message.edit_text(
        f"⏳ جارٍ إرسال الإذاعة لـ {len(user_ids)} مستخدم..."
    )

    if bot is None:
        bot = callback.bot
    svc = BroadcastService(bot)
    result = await svc.send_to_users(
        user_ids=user_ids,
        text="",
        from_chat_id=from_chat,
        message_id=msg_id,
    )
    await callback.message.edit_text(
        f"✅ <b>اكتملت الإذاعة</b>\n\n{result}",
        parse_mode="HTML",
    )
    await callback.answer()
