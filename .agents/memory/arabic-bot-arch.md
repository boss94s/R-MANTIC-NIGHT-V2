---
name: Arabic AI Bot Architecture
description: هيكل منصة الذكاء الاصطناعي العربية على تيليغرام - Aiogram 3.x + SQLAlchemy Async + PostgreSQL
---

## نقطة الدخول
- `main.py` (وليس `bot.py` القديم)
- يُنشئ جداول DB تلقائياً عند أول تشغيل عبر `Base.metadata.create_all`
- يُنشئ الشخصيات والإعدادات الافتراضية عبر `seed_defaults()`

## إعداد pydantic-settings
- `BOT_TOKEN` و`DATABASE_URL` اختياريان في `Settings` (لتجنب crash عند import)
- التحقق من وجودهما يتم في `main()` مع رسالة واضحة

**Why:** pydantic-settings تُنشئ singleton عند import، فإذا كان الحقل required فسيفشل كل import في بيئة بدون env vars.

## هيكل الطبقات
- `bot/database/repositories/` — طبقة CRUD فوق SQLAlchemy Async
- `bot/services/` — منطق أعمال (AIService, BroadcastService, StatisticsService)
- `bot/handlers/{admin,user}/` — Aiogram handlers منظمة حسب الدور
- `bot/middlewares/` — AuthMiddleware (get_or_create user) + RateLimitMiddleware + SubscriptionMiddleware

## نظام الشخصيات
- Character.system_prompt يُضاف كـ system message قبل تاريخ المحادثة
- كل مستخدم لديه selected_character_id في جدول users
- المحادثات مستقلة لكل (user, character)

## الإذاعة
- BroadcastService.send_to_users يستخدم forward_message إذا توفر message_id
- يتجاهل TelegramForbiddenError (حجب البوت) بهدوء

## قواعد الصلاحيات
- IsOwner: OWNER_ID من env فقط
- IsAdmin: OWNER_ID أو موجود في جدول admins
- كلاهما filters وليس middleware
