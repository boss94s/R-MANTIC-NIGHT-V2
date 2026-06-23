from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.base import async_session_factory
from bot.database.repositories import CharacterRepository
from bot.keyboards.admin.characters_kb import (
    characters_manage_kb, characters_list_kb, character_detail_kb, character_create_confirm_kb
)
from bot.states import AdminStates
from bot.utils import logger, helpers

router = Router()
PER_PAGE = 6


@router.callback_query(lambda c: c.data == "admin:characters")
async def characters_panel(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎭 <b>إدارة الشخصيات</b>\n\nاختر من الخيارات:",
        reply_markup=characters_manage_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("char:list:"))
async def characters_list(callback: CallbackQuery):
    page = int(callback.data.split(":")[2])
    async with async_session_factory() as session:
        repo = CharacterRepository(session)
        all_chars = await repo.get_all()
    paged, total_pages = helpers.paginate(all_chars, page, PER_PAGE)
    text = f"📋 <b>الشخصيات</b> — الصفحة {page}/{total_pages}"
    await callback.message.edit_text(
        text,
        reply_markup=characters_list_kb(paged, page, total_pages),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("char:detail:"))
async def character_detail(callback: CallbackQuery):
    char_id = int(callback.data.split(":")[2])
    async with async_session_factory() as session:
        repo = CharacterRepository(session)
        char = await repo.get_by_id(char_id)
    if not char:
        await callback.answer("❌ الشخصية غير موجودة.", show_alert=True)
        return
    status = "✅ نشطة" if char.is_active else "❌ معطّلة"
    text = (
        f"🎭 <b>{char.name}</b>\n\n"
        f"📝 الوصف: {char.description}\n"
        f"🗂 الفئة: {char.category}\n"
        f"🔘 الحالة: {status}\n\n"
        f"🤖 البرومبت:\n<code>{helpers.truncate(char.system_prompt, 200)}</code>"
    )
    await callback.message.edit_text(
        text,
        reply_markup=character_detail_kb(char_id, char.is_active),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("char:toggle:"))
async def toggle_character(callback: CallbackQuery):
    char_id = int(callback.data.split(":")[2])
    async with async_session_factory() as session:
        repo = CharacterRepository(session)
        char = await repo.toggle_active(char_id)
        await session.commit()
    if char:
        status = "✅ تم التفعيل" if char.is_active else "❌ تم التعطيل"
        await callback.answer(f"الشخصية {char.name}: {status}", show_alert=True)
        await character_detail(callback)


@router.callback_query(F.data.startswith("char:delete:"))
async def delete_character(callback: CallbackQuery):
    char_id = int(callback.data.split(":")[2])
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ تأكيد الحذف", callback_data=f"char:delete:confirm:{char_id}"),
            InlineKeyboardButton(text="❌ إلغاء", callback_data=f"char:detail:{char_id}"),
        ]
    ])
    await callback.message.edit_text(
        "⚠️ هل أنت متأكد من حذف هذه الشخصية؟ لا يمكن التراجع.",
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("char:delete:confirm:"))
async def delete_character_confirm(callback: CallbackQuery):
    char_id = int(callback.data.split(":")[3])
    async with async_session_factory() as session:
        repo = CharacterRepository(session)
        char = await repo.get_by_id(char_id)
        if char:
            await repo.delete(char)
            await session.commit()
    await callback.answer("✅ تم حذف الشخصية.", show_alert=True)
    await callback.message.edit_text(
        "🎭 <b>إدارة الشخصيات</b>",
        reply_markup=characters_manage_kb(),
        parse_mode="HTML",
    )


@router.callback_query(lambda c: c.data == "char:create")
async def create_character_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🎭 أرسل <b>اسم</b> الشخصية الجديدة:", parse_mode="HTML")
    await state.set_state(AdminStates.waiting_character_name)
    await callback.answer()


@router.message(AdminStates.waiting_character_name)
async def create_char_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("📝 أرسل <b>وصف</b> الشخصية:", parse_mode="HTML")
    await state.set_state(AdminStates.waiting_character_description)


@router.message(AdminStates.waiting_character_description)
async def create_char_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await message.answer(
        "🤖 أرسل <b>System Prompt</b> (برومبت الشخصية):\n\n"
        "<i>مثال: أنت مساعد ذكي يتحدث العربية الفصحى ويجيب بشكل مفيد ومنظم.</i>",
        parse_mode="HTML",
    )
    await state.set_state(AdminStates.waiting_character_prompt)


@router.message(AdminStates.waiting_character_prompt)
async def create_char_prompt(message: Message, state: FSMContext):
    await state.update_data(system_prompt=message.text.strip())
    await message.answer("🗂 أرسل <b>فئة</b> الشخصية (مثل: عام، تعليم، ترفيه):", parse_mode="HTML")
    await state.set_state(AdminStates.waiting_character_category)


@router.message(AdminStates.waiting_character_category)
async def create_char_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text.strip())
    data = await state.get_data()
    text = (
        f"✅ <b>ملخص الشخصية الجديدة:</b>\n\n"
        f"📛 الاسم: <b>{data['name']}</b>\n"
        f"📝 الوصف: {data['description']}\n"
        f"🗂 الفئة: {data['category']}\n"
        f"🤖 البرومبت: <code>{helpers.truncate(data['system_prompt'], 150)}</code>\n\n"
        f"هل تريد الإنشاء؟"
    )
    await message.answer(text, reply_markup=character_create_confirm_kb(), parse_mode="HTML")


@router.callback_query(lambda c: c.data == "char:create:confirm")
async def create_char_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    async with async_session_factory() as session:
        repo = CharacterRepository(session)
        char = await repo.create_character(
            name=data["name"],
            description=data["description"],
            system_prompt=data["system_prompt"],
            category=data.get("category", "عام"),
        )
        await session.commit()
    await callback.message.edit_text(
        f"✅ تم إنشاء شخصية <b>{char.name}</b> بنجاح!",
        reply_markup=characters_manage_kb(),
        parse_mode="HTML",
    )
    logger.info(f"تم إنشاء شخصية: {char.name}")
    await callback.answer()


@router.callback_query(F.data.startswith("char:edit:name:"))
async def edit_char_name_start(callback: CallbackQuery, state: FSMContext):
    char_id = int(callback.data.split(":")[3])
    await state.update_data(edit_char_id=char_id)
    await callback.message.edit_text("✏️ أرسل الاسم الجديد للشخصية:")
    await state.set_state(AdminStates.editing_character_name)
    await callback.answer()


@router.message(AdminStates.editing_character_name)
async def edit_char_name_save(message: Message, state: FSMContext):
    data = await state.get_data()
    char_id = data["edit_char_id"]
    await state.clear()
    async with async_session_factory() as session:
        repo = CharacterRepository(session)
        await repo.update_character(char_id, name=message.text.strip())
        await session.commit()
    await message.answer("✅ تم تحديث اسم الشخصية.")


@router.callback_query(F.data.startswith("char:edit:desc:"))
async def edit_char_desc_start(callback: CallbackQuery, state: FSMContext):
    char_id = int(callback.data.split(":")[3])
    await state.update_data(edit_char_id=char_id)
    await callback.message.edit_text("📝 أرسل الوصف الجديد للشخصية:")
    await state.set_state(AdminStates.editing_character_description)
    await callback.answer()


@router.message(AdminStates.editing_character_description)
async def edit_char_desc_save(message: Message, state: FSMContext):
    data = await state.get_data()
    char_id = data["edit_char_id"]
    await state.clear()
    async with async_session_factory() as session:
        repo = CharacterRepository(session)
        await repo.update_character(char_id, description=message.text.strip())
        await session.commit()
    await message.answer("✅ تم تحديث وصف الشخصية.")


@router.callback_query(F.data.startswith("char:edit:prompt:"))
async def edit_char_prompt_start(callback: CallbackQuery, state: FSMContext):
    char_id = int(callback.data.split(":")[3])
    await state.update_data(edit_char_id=char_id)
    await callback.message.edit_text("🤖 أرسل البرومبت الجديد للشخصية:")
    await state.set_state(AdminStates.editing_character_prompt)
    await callback.answer()


@router.message(AdminStates.editing_character_prompt)
async def edit_char_prompt_save(message: Message, state: FSMContext):
    data = await state.get_data()
    char_id = data["edit_char_id"]
    await state.clear()
    async with async_session_factory() as session:
        repo = CharacterRepository(session)
        await repo.update_character(char_id, system_prompt=message.text.strip())
        await session.commit()
    await message.answer("✅ تم تحديث برومبت الشخصية.")
