from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.base import async_session_factory
from bot.database.repositories import ChannelRepository
from bot.keyboards.admin.channels_kb import channels_manage_kb, channels_list_kb
from bot.states import AdminStates
from bot.utils import logger

router = Router()


@router.callback_query(lambda c: c.data == "admin:channels")
async def channels_panel(callback: CallbackQuery):
    await callback.message.edit_text(
        "📺 <b>الاشتراك الإجباري</b>\n\nإدارة قنوات الاشتراك الإجباري:",
        reply_markup=channels_manage_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "channel:list")
async def channels_list(callback: CallbackQuery):
    async with async_session_factory() as session:
        repo = ChannelRepository(session)
        channels = await repo.get_all()
    if not channels:
        await callback.answer("لا توجد قنوات مضافة.", show_alert=True)
        return
    await callback.message.edit_text(
        "📺 <b>قائمة القنوات</b>:",
        reply_markup=channels_list_kb(channels),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "channel:add")
async def add_channel_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📺 أضف البوت كمشرف في القناة أولاً، ثم أرسل:\n\n"
        "<code>channel_id | اسم_القناة | @username</code>\n\n"
        "<i>مثال: -1001234567890 | قناة الاختبار | @test_channel</i>",
        parse_mode="HTML",
    )
    await state.set_state(AdminStates.waiting_add_channel)
    await callback.answer()


@router.message(AdminStates.waiting_add_channel)
async def add_channel_execute(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    parts = [p.strip() for p in message.text.strip().split("|")]
    if len(parts) < 2:
        await message.answer(
            "❌ التنسيق غير صحيح. أرسل:\n<code>channel_id | اسم_القناة | @username</code>",
            parse_mode="HTML",
        )
        return
    try:
        ch_id = int(parts[0])
        ch_name = parts[1]
        ch_username = parts[2] if len(parts) > 2 else ""
    except ValueError:
        await message.answer("❌ ID القناة يجب أن يكون رقماً.")
        return

    try:
        chat = await bot.get_chat(ch_id)
        ch_name = chat.title or ch_name
        ch_username = chat.username or ch_username
    except Exception:
        pass

    async with async_session_factory() as session:
        repo = ChannelRepository(session)
        ch = await repo.add_channel(ch_id, ch_name, ch_username)
        await session.commit()

    await message.answer(
        f"✅ تمت إضافة القناة <b>{ch_name}</b>.",
        parse_mode="HTML",
    )
    logger.info(f"تمت إضافة قناة: {ch_id}")


@router.callback_query(F.data.startswith("channel:toggle:"))
async def toggle_channel(callback: CallbackQuery):
    ch_id = int(callback.data.split(":")[2])
    async with async_session_factory() as session:
        repo = ChannelRepository(session)
        ch = await repo.toggle_required(ch_id)
        await session.commit()
    if ch:
        status = "✅ مفعّل" if ch.is_required else "❌ معطّل"
        await callback.answer(f"الحالة: {status}", show_alert=True)
    await channels_list(callback)


@router.callback_query(F.data.startswith("channel:delete:"))
async def delete_channel(callback: CallbackQuery):
    ch_id = int(callback.data.split(":")[2])
    async with async_session_factory() as session:
        repo = ChannelRepository(session)
        result = await repo.remove_channel(ch_id)
        await session.commit()
    if result:
        await callback.answer("✅ تم حذف القناة.", show_alert=True)
    else:
        await callback.answer("❌ القناة غير موجودة.", show_alert=True)
    await channels_list(callback)
