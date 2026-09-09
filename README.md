# Dorar Tafsir MCP — v2

مشروع MCP للقراءة فقط، مصمم على نمط الموصلات المعرفية مثل Bahouth MCP، ويعرض واجهة ويب وEndpoint Streamable HTTP.

## المكونات

- `app.py`: خادم FastAPI + MCP.
- `/`: صفحة تعريفية.
- `/health`: فحص الخدمة.
- `/mcp`: Endpoint MCP عبر Streamable HTTP.
- أدوات MCP:
  - `get_ayah`
  - `get_ayah_tafsir`
  - `get_surah_tafsir`
  - `search_tafsir`
  - `open_source`
  - `list_capabilities`

## تشغيل محلي

يتطلب Python 3.10+.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app:web --host 127.0.0.1 --port 8000
```

ثم:
- الموقع: http://127.0.0.1:8000/
- الفحص: http://127.0.0.1:8000/health
- MCP: http://127.0.0.1:8000/mcp

## اختبار MCP

يمكن استعمال MCP Inspector مع عنوان:
`http://127.0.0.1:8000/mcp`

## النشر

المشروع يتضمن `Dockerfile` و`render.yaml` كنقطة بداية لنشر خدمة عامة HTTPS.

بعد النشر يصبح الرابط:
`https://YOUR-DOMAIN/mcp`

وهذا هو الرابط الذي يستخدمه العميل الداعم لـ MCP.

## تنبيه علمي وتقني

النسخة الحالية تعتمد على صفحات الويب العامة في الدرر السنية، وليست API رسمية للدرر. بنية صفحات الموقع قد تتغير، لذلك يجب اختبار الاستخراج بعد النشر. لا تحفظ هذه النسخة محتوى الدرر في قاعدة بيانات، ولا تغيّر بيانات الموقع.

كما ينبغي مراجعة شروط استخدام الموقع وسياسة الطلبات قبل النشر العام واسع النطاق.
