from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.base import async_session_factory
from bot.database.repositories import (
    ConversationRepository, MessageRepository, CharacterRepository, UserRepository
)
from bot.keyboards.user.conversations_kb import conversations_kb, conversation_detail_kb
from bot.keyboards.user.main_kb import user_main_kb
from bot.states import UserStates
from bot.utils import helpers

router = Router()
PER_PAGE = 5


@router.message(Command("new"))
@router.callback_query(lambda c: c.data == "user:new_chat")
async def new_conversation(event, db_user=None):
    if not db_user:
        return
    async with async_session_factory() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(
            event.from_user.id if isinstance(event, Message) else event.from_user.id
        )
        if not user:
            return
        conv_repo = ConversationRepository(session)
        char_id = user.selected_character_id
        char_name = "الذكاء الاصطناعي"
        if char_id:
            char_repo = CharacterRepository(session)
            char = await char_repo.get_by_id(char_id)
            if char:
                char_name = char.name
        await conv_repo.create_conversation(
            user_id=user.id,
            character_id=char_id,
            title=f"محادثة مع {char_name}",
        )
        await session.commit()

    text = f"✅ <b>تم إنشاء محادثة جديدة</b>\n\nأرسل رسالتك للبدء!"
    if isinstance(event, Message):
        await event.answer(text, reply_markup=user_main_kb(), parse_mode="HTML")
    else:
        await event.message.edit_text(text, reply_markup=user_main_kb(), parse_mode="HTML")
        await event.answer()


@router.message(Command("clear"))
@router.callback_query(lambda c: c.data == "user:clear_chat")
async def clear_conversation(event, db_user=None):
    if not db_user:
        return
    async with async_session_factory() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(event.from_user.id)
        if not user:
            return
        conv_repo = ConversationRepository(session)
        conv = await conv_repo.get_latest_for_user(user.id, user.selected_character_id)
        if conv:
            msg_repo = MessageRepository(session)
            await msg_repo.delete_conversation_messages(conv.id)
            await session.commit()

    text = "🗑 <b>تم مسح المحادثة الحالية.</b>"
    if isinstance(event, Message):
        await event.answer(text, reply_markup=user_main_kb(), parse_mode="HTML")
    else:
        await event.message.edit_text(text, reply_markup=user_main_kb(), parse_mode="HTML")
        await event.answer()


@router.callback_query(lambda c: c.data == "user:conversations")
async def show_conversations(callback: CallbackQuery, db_user=None):
    if not db_user:
        return
    async with async_session_factory() as session:
        conv_repo = ConversationRepository(session)
        convs = await conv_repo.get_user_conversations(db_user.id)

    if not convs:
        await callback.message.edit_text(
            "💬 لا توجد محادثات.\n\nابدأ محادثة جديدة!",
            reply_markup=user_main_kb(),
        )
        await callback.answer()
        return

    paged, total_pages = helpers.paginate(convs, 1, PER_PAGE)
    await callback.message.edit_text(
        f"💬 <b>محادثاتي</b>\n\n{len(convs)} محادثة",
        reply_markup=conversations_kb(paged, 1, total_pages),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("conv:page:"))
async def conversations_page(callback: CallbackQuery, db_user=None):
    page = int(callback.data.split(":")[2])
    if not db_user:
        return
    async with async_session_factory() as session:
        conv_repo = ConversationRepository(session)
        convs = await conv_repo.get_user_conversations(db_user.id)
    paged, total_pages = helpers.paginate(convs, page, PER_PAGE)
    await callback.message.edit_text(
        f"💬 <b>محادثاتي</b> — الصفحة {page}/{total_pages}",
        reply_markup=conversations_kb(paged, page, total_pages),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("conv:open:"))
async def open_conversation(callback: CallbackQuery, db_user=None):
    conv_id = int(callback.data.split(":")[2])
    if not db_user:
        return
    async with async_session_factory() as session:
        conv_repo = ConversationRepository(session)
        conv = await conv_repo.get_by_id_and_user(conv_id, db_user.id)
    if not conv:
        await callback.answer("❌ المحادثة غير موجودة.", show_alert=True)
        return
    char_name = conv.character.name if conv.character else "الذكاء الاصطناعي"
    msg_count = len(conv.messages)
    text = (
        f"💬 <b>{conv.title}</b>\n\n"
        f"🎭 الشخصية: {char_name}\n"
        f"📨 الرسائل: {msg_count}\n"
        f"📅 التاريخ: {conv.created_at.strftime('%Y-%m-%d')}"
    )
    await callback.message.edit_text(
        text, reply_markup=conversation_detail_kb(conv_id), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("conv:resume:"))
async def resume_conversation(callback: CallbackQuery, db_user=None):
    conv_id = int(callback.data.split(":")[2])
    if not db_user:
        return
    async with async_session_factory() as session:
        conv_repo = ConversationRepository(session)
        conv = await conv_repo.get_by_id_and_user(conv_id, db_user.id)
        if conv:
            user_repo = UserRepository(session)
            await user_repo.set_character(callback.from_user.id, conv.character_id)
            await session.commit()

    await callback.message.edit_text(
        f"▶️ <b>استكمال المحادثة</b>\n\nأرسل رسالتك.",
        reply_markup=user_main_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("conv:rename:"))
async def rename_conversation_start(callback: CallbackQuery, state: FSMContext):
    conv_id = int(callback.data.split(":")[2])
    await state.update_data(rename_conv_id=conv_id)
    await callback.message.edit_text("✏️ أرسل الاسم الجديد للمحادثة:")
    await state.set_state(UserStates.renaming_conversation)
    await callback.answer()


@router.message(UserStates.renaming_conversation)
async def rename_conversation_save(message: Message, state: FSMContext, db_user=None):
    data = await state.get_data()
    conv_id = data.get("rename_conv_id")
    await state.clear()
    if not conv_id or not db_user:
        return
    async with async_session_factory() as session:
        conv_repo = ConversationRepository(session)
        conv = await conv_repo.get_by_id_and_user(conv_id, db_user.id)
        if conv:
            await conv_repo.rename_conversation(conv_id, message.text.strip())
            await session.commit()
    await message.answer("✅ تم تغيير اسم المحادثة.", reply_markup=user_main_kb())


@router.callback_query(F.data.startswith("conv:delete:"))
async def delete_conversation(callback: CallbackQuery, db_user=None):
    conv_id = int(callback.data.split(":")[2])
    if not db_user:
        return
    async with async_session_factory() as session:
        conv_repo = ConversationRepository(session)
        conv = await conv_repo.get_by_id_and_user(conv_id, db_user.id)
        if conv:
            await conv_repo.delete(conv)
            await session.commit()
    await callback.answer("✅ تم حذف المحادثة.", show_alert=True)
    await callback.message.edit_text(
        "🗑 تم حذف المحادثة.", reply_markup=user_main_kb()
    )
