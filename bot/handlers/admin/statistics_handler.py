from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot.services.statistics_service import StatisticsService
from bot.utils.helpers import format_number

router = Router()


@router.callback_query(lambda c: c.data == "admin:stats")
async def show_statistics(callback: CallbackQuery):
    svc = StatisticsService()
    stats = await svc.get_full_stats()

    text = (
        "📊 <b>إحصائيات المنصة</b>\n\n"
        f"👥 إجمالي المستخدمين: <b>{format_number(stats['total_users'])}</b>\n"
        f"💬 إجمالي الرسائل: <b>{format_number(stats['total_messages'])}</b>\n"
        f"🗨 إجمالي المحادثات: <b>{format_number(stats['total_conversations'])}</b>\n"
        f"🎭 الشخصيات النشطة: <b>{format_number(stats['total_characters'])}</b>\n\n"
        f"📅 النشطون يومياً: <b>{format_number(stats['daily_active'])}</b>\n"
        f"📆 النشطون شهرياً: <b>{format_number(stats['monthly_active'])}</b>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 تحديث", callback_data="admin:stats")],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="admin:main")],
    ])

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()
