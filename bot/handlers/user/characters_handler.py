from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.database.base import async_session_factory
from bot.database.repositories import CharacterRepository, UserRepository, ConversationRepository
from bot.keyboards.user.characters_kb import characters_select_kb, character_confirm_kb
from bot.keyboards.user.main_kb import user_main_kb
from bot.utils import helpers

router = Router()
PER_PAGE = 5


async def show_characters(event, page: int = 1, selected_id: int = None):
    async with async_session_factory() as session:
        repo = CharacterRepository(session)
        chars = await repo.get_active_characters()

    if not chars:
        text = "❌ لا توجد شخصيات متاحة حالياً."
        if isinstance(event, Message):
            await event.answer(text)
        else:
            await event.message.edit_text(text)
        return

    paged, total_pages = helpers.paginate(chars, page, PER_PAGE)
    text = (
        f"🎭 <b>اختر شخصية</b>\n\n"
        f"الصفحة {page}/{total_pages} — {len(chars)} شخصية متاحة"
    )
    kb = characters_select_kb(paged, page, total_pages, selected_id)

    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await event.answer()


@router.message(Command("chars"))
@router.callback_query(lambda c: c.data == "user:characters")
async def characters_menu(event, db_user=None):
    selected_id = db_user.selected_character_id if db_user else None
    await show_characters(event, 1, selected_id)


@router.callback_query(F.data.startswith("chars_page:"))
async def characters_page(callback: CallbackQuery, db_user=None):
    page = int(callback.data.split(":")[1])
    selected_id = db_user.selected_character_id if db_user else None
    await show_characters(callback, page, selected_id)


@router.callback_query(F.data.startswith("select_char:"))
async def select_character_preview(callback: CallbackQuery):
    char_id = int(callback.data.split(":")[1])
    async with async_session_factory() as session:
        repo = CharacterRepository(session)
        char = await repo.get_by_id(char_id)

    if not char:
        await callback.answer("❌ الشخصية غير موجودة.", show_alert=True)
        return

    text = (
        f"🎭 <b>{char.name}</b>\n\n"
        f"📝 {char.description}\n\n"
        f"🗂 الفئة: {char.category}\n\n"
        f"هل تريد اختيار هذه الشخصية؟"
    )

    if char.avatar_url:
        try:
            await callback.message.answer_photo(
                photo=char.avatar_url,
                caption=text,
                reply_markup=character_confirm_kb(char_id),
                parse_mode="HTML",
            )
        except Exception:
            await callback.message.edit_text(text, reply_markup=character_confirm_kb(char_id), parse_mode="HTML")
    else:
        await callback.message.edit_text(text, reply_markup=character_confirm_kb(char_id), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_char:"))
async def confirm_character(callback: CallbackQuery, db_user=None):
    char_id = int(callback.data.split(":")[1])

    async with async_session_factory() as session:
        char_repo = CharacterRepository(session)
        char = await char_repo.get_by_id(char_id)
        if not char:
            await callback.answer("❌ الشخصية غير موجودة.", show_alert=True)
            return

        user_repo = UserRepository(session)
        await user_repo.set_character(callback.from_user.id, char_id)

        conv_repo = ConversationRepository(session)
        await conv_repo.create_conversation(
            user_id=db_user.id if db_user else 0,
            character_id=char_id,
            title=f"محادثة مع {char.name}",
        )
        await session.commit()

    text = (
        f"✅ <b>تم اختيار {char.name}</b>\n\n"
        f"يمكنك الآن بدء المحادثة! اكتب رسالتك."
    )
    try:
        await callback.message.edit_text(text, reply_markup=user_main_kb(), parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, reply_markup=user_main_kb(), parse_mode="HTML")
    await callback.answer(f"✅ اخترت {char.name}!")
