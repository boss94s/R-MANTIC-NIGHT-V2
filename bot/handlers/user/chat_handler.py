from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.database.base import async_session_factory
from bot.database.repositories import (
    UserRepository, ConversationRepository, MessageRepository,
    CharacterRepository, SettingRepository
)
from bot.services.ai_service import AIService
from bot.config import settings
from bot.utils import logger

router = Router()
ai_service = AIService()


async def get_or_create_conversation(user_id: int, telegram_id: int):
    async with async_session_factory() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(telegram_id)
        if not user:
            return None, None, None

        conv_repo = ConversationRepository(session)
        conv = await conv_repo.get_latest_for_user(user.id, user.selected_character_id)

        char = None
        if user.selected_character_id:
            char_repo = CharacterRepository(session)
            char = await char_repo.get_by_id(user.selected_character_id)

        if not conv:
            char_name = char.name if char else "الذكاء الاصطناعي"
            conv = await conv_repo.create_conversation(
                user_id=user.id,
                character_id=user.selected_character_id,
                title=f"محادثة مع {char_name}",
            )
            await session.commit()

        msg_repo = MessageRepository(session)
        messages = await msg_repo.get_recent_messages(conv.id, limit=20)

        history = [{"role": m.role, "content": m.content} for m in messages]
        system_prompt = char.system_prompt if char else ""

        return conv.id, history, system_prompt


@router.message(Command("new"))
async def handle_new(message: Message):
    pass


@router.message(lambda m: m.text and not m.text.startswith("/"))
async def handle_message(message: Message, db_user=None):
    if not db_user:
        return

    maintenance = False
    async with async_session_factory() as session:
        setting_repo = SettingRepository(session)
        maintenance = await setting_repo.get_bool("maintenance_mode")

    if maintenance and not db_user.is_admin and not db_user.is_owner:
        await message.answer("🔧 البوت في وضع الصيانة. يرجى المحاولة لاحقاً.")
        return

    if not settings.API_KEY:
        await message.answer("❌ لم يتم إعداد مفتاح API. تواصل مع المشرف.")
        return

    user_text = message.text.strip()
    conv_id, history, system_prompt = await get_or_create_conversation(
        db_user.id, message.from_user.id
    )
    if not conv_id:
        await message.answer("❌ حدث خطأ. يرجى المحاولة مجدداً.")
        return

    thinking_msg = await message.answer("⌛ جارٍ المعالجة...")

    messages_for_ai = ai_service.build_messages(history, user_text, system_prompt)

    full_response = ""
    chunk_buffer = ""
    last_edit_len = 0

    try:
        async for chunk in ai_service.chat_stream(messages_for_ai):
            full_response += chunk
            chunk_buffer += chunk
            if len(full_response) - last_edit_len >= 100 or "\n" in chunk_buffer:
                try:
                    display = full_response + " ▌"
                    if len(display) <= 4096:
                        await thinking_msg.edit_text(display)
                        last_edit_len = len(full_response)
                        chunk_buffer = ""
                except Exception:
                    pass

        if not full_response:
            await thinking_msg.edit_text("❌ لم يتم الحصول على رد. يرجى المحاولة لاحقاً.")
            return

        if len(full_response) <= 4096:
            await thinking_msg.edit_text(full_response)
        else:
            await thinking_msg.delete()
            for i in range(0, len(full_response), 4096):
                await message.answer(full_response[i:i + 4096])

        async with async_session_factory() as session:
            msg_repo = MessageRepository(session)
            await msg_repo.add_message(conv_id, "user", user_text)
            await msg_repo.add_message(conv_id, "assistant", full_response)
            user_repo = UserRepository(session)
            await user_repo.increment_messages(message.from_user.id)
            await session.commit()

        logger.debug(f"رسالة من {message.from_user.id}: {len(user_text)} حرف")

    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة: {e}")
        try:
            await thinking_msg.edit_text("❌ حدث خطأ. يرجى المحاولة مرة أخرى.")
        except Exception:
            await message.answer("❌ حدث خطأ. يرجى المحاولة مرة أخرى.")
