# منصة الذكاء الاصطناعي العربية — Telegram Bot

بوت تيليغرام عربي متكامل مبني على Aiogram 3.x مع نظام شخصيات متعدد وإدارة محادثات ولوحة تحكم إدارية شاملة.

## ⚙️ إعداد المشروع

### المتغيرات المطلوبة (أضفها في Secrets)

| المتغير | الوصف | مطلوب |
|---------|-------|--------|
| `BOT_TOKEN` | توكن البوت من [@BotFather](https://t.me/BotFather) | ✅ مطلوب |
| `DATABASE_URL` | رابط PostgreSQL (مُعيَّن تلقائياً) | ✅ مطلوب |
| `API_KEY` | مفتاح OpenAI أو أي API متوافق | ✅ للدردشة |

### المتغيرات الاختيارية

| المتغير | الوصف | الافتراضي |
|---------|-------|-----------|
| `OWNER_ID` | ID المالك على تيليغرام | — |
| `BASE_URL` | رابط API (للنماذج الأخرى) | `https://api.openai.com/v1/chat/completions` |
| `MODEL` | نموذج الذكاء الاصطناعي | `gpt-4o-mini` |
| `RATE_LIMIT_MESSAGES` | عدد الرسائل المسموح بها | `30` |
| `RATE_LIMIT_WINDOW` | نافذة التحديد (بالثواني) | `60` |
| `FREE_MESSAGES` | رسائل مجانية لكل مستخدم | `100` |

## 🚀 خطوات التشغيل

1. أضف `BOT_TOKEN` في Secrets (أيقونة القفل 🔒)
2. أضف `API_KEY` في Secrets
3. أضف `OWNER_ID` (ID حسابك على تيليغرام)
4. اضغط **Run** لتشغيل البوت

## 🏗️ هيكل المشروع

```
main.py                    # نقطة الدخول الرئيسية
bot/
├── config/
│   └── settings.py        # إعدادات pydantic-settings
├── database/
│   ├── base.py            # SQLAlchemy async engine
│   ├── models/            # نماذج قاعدة البيانات
│   └── repositories/      # طبقة الوصول للبيانات
├── handlers/
│   ├── admin/             # handlers الإدارة
│   └── user/              # handlers المستخدم
├── services/              # منطق الأعمال
├── middlewares/           # Auth, RateLimit, Subscription
├── filters/               # IsAdmin, IsOwner
├── states/                # FSM states
├── keyboards/             # لوحات المفاتيح
└── utils/                 # أدوات مساعدة
```

## 🎭 نظام الشخصيات

يتضمن البوت 3 شخصيات افتراضية تُنشأ تلقائياً:
- **المساعد الذكي** — مساعد عام
- **المعلم التعليمي** — متخصص في الشرح
- **المبرمج المساعد** — خبير في البرمجة

## 🛡️ الصلاحيات

- **المالك (Owner)**: صلاحيات كاملة
- **المشرف (Admin)**: إدارة المستخدمين والشخصيات
- **المستخدم (User)**: الدردشة وإدارة المحادثات

## 📋 أوامر الإدارة

- `/admin` — لوحة التحكم (للمشرفين)

## 📋 أوامر المستخدم

- `/start` — بدء البوت
- `/menu` — القائمة الرئيسية
- `/new` — محادثة جديدة
- `/clear` — مسح المحادثة
- `/chars` — اختيار شخصية
- `/help` — المساعدة

## User Preferences

- Import paths updated from `aient.aient.*` → `aient.*` (PyPI package paths)
- The bot uses Arabic as the primary UI language
- All admin messages and UI are in Arabic
- Character system inspired by Character.ai with custom system prompts
