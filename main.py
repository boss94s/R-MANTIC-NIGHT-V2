import asyncio
import sys
import os
sys.dont_write_bytecode = True

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.database.base import engine, Base
from bot.database.models import (
    User, Admin, Character, Conversation, Message, Channel, Setting, Statistics
)
from bot.handlers import get_main_router
from bot.middlewares import AuthMiddleware, RateLimitMiddleware, SubscriptionMiddleware
from bot.utils import logger


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ تم تهيئة قاعدة البيانات")


async def seed_defaults():
    from bot.database.base import async_session_factory
    from bot.database.repositories import SettingRepository, CharacterRepository
    async with async_session_factory() as session:
        setting_repo = SettingRepository(session)
        existing = await setting_repo.get("bot_name")
        if not existing:
            await setting_repo.set("bot_name", settings.BOT_NAME)
            await setting_repo.set("welcome", settings.WELCOME_MESSAGE)
            await setting_repo.set("free_messages", str(settings.FREE_MESSAGES))
            await setting_repo.set("maintenance_mode", "false")

        char_repo = CharacterRepository(session)
        count = await char_repo.count_active()
        if count == 0:
            await char_repo.create_character(
                name="المساعد الذكي",
                description="مساعد ذكاء اصطناعي متعدد الأغراض يتحدث العربية",
                system_prompt=(
                    "أنت مساعد ذكاء اصطناعي متطور يتحدث العربية الفصحى. "
                    "تجيب بشكل مفيد ومنظم ودقيق. تحترم الثقافة العربية والإسلامية. "
                    "إذا لم تعرف إجابة، تقول ذلك بصدق."
                ),
                category="عام",
            )
            await char_repo.create_character(
                name="المعلم التعليمي",
                description="مساعد تعليمي متخصص في الشرح والتوضيح",
                system_prompt=(
                    "أنت معلم متخصص وخبير في الشرح والتوضيح. "
                    "تستخدم أمثلة واضحة ومبسطة. تشجع المتعلمين وتساعدهم بصبر. "
                    "تتحدث العربية الفصحى وتبسّط المفاهيم الصعبة."
                ),
                category="تعليم",
            )
            await char_repo.create_character(
                name="المبرمج المساعد",
                description="خبير في البرمجة والتقنية",
                system_prompt=(
                    "أنت مبرمج خبير ومتخصص في التقنية. تساعد في كتابة الكود وشرحه وتصحيح الأخطاء. "
                    "تدعم جميع لغات البرمجة وتشرح بالعربية والإنجليزية. "
                    "تكتب كوداً نظيفاً وقابلاً للصيانة."
                ),
                category="تقنية",
            )
        await session.commit()
    logger.info("✅ تم تهيئة الإعدادات الافتراضية")


async def on_startup(bot: Bot):
    logger.info("🚀 البوت يبدأ...")
    await init_db()
    await seed_defaults()
    me = await bot.get_me()
    logger.info(f"✅ البوت متصل: @{me.username} ({me.id})")
    if settings.OWNER_ID:
        try:
            await bot.send_message(
                settings.OWNER_ID,
                "✅ <b>البوت بدأ بنجاح!</b>\n\n"
                f"🤖 @{me.username}\n"
                "استخدم /admin للوصول للوحة التحكم.",
                parse_mode="HTML",
            )
        except Exception:
            pass


async def on_shutdown(bot: Bot):
    logger.info("🛑 إيقاف البوت...")
    await bot.session.close()


async def main():
    if not settings.BOT_TOKEN:
        logger.error("=" * 60)
        logger.error("❌ BOT_TOKEN غير محدد!")
        logger.error("الرجاء تعيين متغير البيئة BOT_TOKEN في Secrets")
        logger.error("احصل على التوكن من @BotFather على تيليغرام")
        logger.error("=" * 60)
        sys.exit(1)

    if not settings.DATABASE_URL:
        logger.error("❌ DATABASE_URL غير محدد!")
        sys.exit(1)

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    main_router = get_main_router()
    dp.include_router(main_router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("🔄 بدء الاستقبال (Polling)...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
