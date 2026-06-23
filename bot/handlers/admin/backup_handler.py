import os
import subprocess
from datetime import datetime
from aiogram import Router, Bot
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import settings
from bot.utils import logger

router = Router()


def backup_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 إنشاء نسخة احتياطية", callback_data="backup:create")],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="admin:main")],
    ])


@router.callback_query(lambda c: c.data == "admin:backup")
async def backup_panel(callback: CallbackQuery):
    await callback.message.edit_text(
        "🗄 <b>النسخ الاحتياطي</b>\n\nيمكنك إنشاء نسخة احتياطية من قاعدة البيانات:",
        reply_markup=backup_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "backup:create")
async def create_backup(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != settings.OWNER_ID:
        await callback.answer("❌ هذه الصلاحية للمالك فقط.", show_alert=True)
        return

    await callback.message.edit_text("⏳ جارٍ إنشاء النسخة الاحتياطية...")
    await callback.answer()

    os.makedirs("backups", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/backup_{timestamp}.sql"

    db_url = settings.DATABASE_URL
    try:
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.PGPASSWORD if hasattr(settings, "PGPASSWORD") else ""

        cmd = [
            "pg_dump",
            "--no-password",
            "--format=plain",
            "--file", backup_file,
            db_url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=120)

        if result.returncode != 0:
            raise Exception(result.stderr)

        file_size = os.path.getsize(backup_file)
        size_kb = file_size / 1024

        doc = FSInputFile(backup_file, filename=f"backup_{timestamp}.sql")
        await bot.send_document(
            chat_id=callback.from_user.id,
            document=doc,
            caption=(
                f"✅ <b>نسخة احتياطية ناجحة</b>\n\n"
                f"📅 التاريخ: {timestamp}\n"
                f"📦 الحجم: {size_kb:.1f} كيلوبايت"
            ),
            parse_mode="HTML",
        )
        await callback.message.edit_text(
            "✅ تم إنشاء وإرسال النسخة الاحتياطية بنجاح!",
            reply_markup=backup_kb(),
        )
        logger.info(f"تم إنشاء نسخة احتياطية: {backup_file}")
    except Exception as e:
        logger.error(f"خطأ في النسخ الاحتياطي: {e}")
        await callback.message.edit_text(
            f"❌ فشل إنشاء النسخة الاحتياطية.\nالخطأ: {str(e)[:200]}",
            reply_markup=backup_kb(),
        )
