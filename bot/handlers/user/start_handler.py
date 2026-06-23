from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from bot.database.base import async_session_factory
from bot.database.repositories import UserRepository, SettingRepository, CharacterRepository
from bot.keyboards.user.main_kb import user_main_kb
from bot.keyboards.user.characters_kb import characters_select_kb
from bot.config import settings
from bot.utils import logger, helpers

router = Router()


async def get_welcome_text(session, user_name: str) -> str:
    repo = SettingRepository(session)
    welcome = await repo.get("welcome", settings.WELCOME_MESSAGE)
    bot_name = await repo.get("bot_name", settings.BOT_NAME)
    return (
        f"🌟 <b>{bot_name}</b>\n\n"
        f"أهلاً وسهلاً <b>{user_name}</b>! 👋\n\n"
        f"{welcome}"
    )


@router.message(CommandStart())
async def cmd_start(message: Message, db_user=None, is_new_user: bool = False):
    async with async_session_factory() as session:
        text = await get_welcome_text(session, message.from_user.first_name)

        if is_new_user:
            char_repo = CharacterRepository(session)
            chars = await char_repo.get_active_characters()
            if chars:
                text += "\n\n🎭 ابدأ باختيار شخصية للتحدث معها:"
                paged, total = helpers.paginate(chars, 1, 5)
                await message.answer(
                    text,
                    reply_markup=characters_select_kb(paged, 1, total),
                    parse_mode="HTML",
                )
                return

    await message.answer(text, reply_markup=user_main_kb(), parse_mode="HTML")


@router.message(Command("menu"))
@router.callback_query(lambda c: c.data == "user:main")
async def show_main_menu(event, db_user=None):
    if isinstance(event, Message):
        await event.answer(
            "📋 <b>القائمة الرئيسية</b>",
            reply_markup=user_main_kb(),
            parse_mode="HTML",
        )
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(
            "📋 <b>القائمة الرئيسية</b>",
            reply_markup=user_main_kb(),
            parse_mode="HTML",
        )
        await event.answer()


@router.callback_query(lambda c: c.data == "user:about")
async def about_bot(callback: CallbackQuery):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    async with async_session_factory() as session:
        repo = SettingRepository(session)
        bot_name = await repo.get("bot_name", settings.BOT_NAME)
    text = (
        f"ℹ️ <b>عن {bot_name}</b>\n\n"
        f"🤖 منصة ذكاء اصطناعي عربية متكاملة\n"
        f"🎭 تدعم شخصيات متعددة\n"
        f"💬 محادثات ذكية باللغة العربية\n"
        f"⚡ مدعومة بأحدث نماذج الذكاء الاصطناعي\n\n"
        f"النموذج الحالي: <code>{settings.MODEL}</code>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="user:main")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "📖 <b>مساعدة</b>\n\n"
        "الأوامر المتاحة:\n"
        "/start — بدء البوت\n"
        "/menu — القائمة الرئيسية\n"
        "/new — محادثة جديدة\n"
        "/clear — مسح المحادثة الحالية\n"
        "/chars — اختيار شخصية\n"
        "/help — المساعدة\n\n"
        "💬 يمكنك فقط إرسال رسالتك وسيرد البوت مباشرةً."
    )
    await message.answer(text, parse_mode="HTML")
