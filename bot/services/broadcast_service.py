from typing import List, Optional
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from bot.utils import logger


class BroadcastResult:
    def __init__(self, total: int, success: int, failed: int):
        self.total = total
        self.success = success
        self.failed = failed

    def __str__(self) -> str:
        return (
            f"📊 نتيجة الإذاعة:\n"
            f"👥 المجموع: {self.total}\n"
            f"✅ نجح: {self.success}\n"
            f"❌ فشل: {self.failed}"
        )


class BroadcastService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_to_users(
        self,
        user_ids: List[int],
        text: str,
        parse_mode: str = "HTML",
        from_chat_id: Optional[int] = None,
        message_id: Optional[int] = None,
    ) -> BroadcastResult:
        success = 0
        failed = 0

        for uid in user_ids:
            try:
                if from_chat_id and message_id:
                    await self.bot.forward_message(
                        chat_id=uid,
                        from_chat_id=from_chat_id,
                        message_id=message_id,
                    )
                else:
                    await self.bot.send_message(uid, text, parse_mode=parse_mode)
                success += 1
            except TelegramForbiddenError:
                failed += 1
                logger.debug(f"المستخدم {uid} حجب البوت")
            except TelegramBadRequest as e:
                failed += 1
                logger.warning(f"طلب خاطئ للمستخدم {uid}: {e}")
            except Exception as e:
                failed += 1
                logger.error(f"خطأ في إرسال الإذاعة للمستخدم {uid}: {e}")

        result = BroadcastResult(
            total=len(user_ids),
            success=success,
            failed=failed,
        )
        logger.info(f"اكتملت الإذاعة: {result}")
        return result
