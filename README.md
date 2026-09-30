# AL-KHALLAQI — وكيل الذكاء الاصطناعي الإبداعي

> **الإبداع بلا حدود**

مطوّره: **Hussein Ghallab**

## المزايا

- وكيل ReAct حقيقي بأدوات فعلية
- توليد صور / فيديو / شعارات / هويات بصرية
- توليد نصوص إبداعية وسيناريوهات
- بحث مرجعي
- بناء APK (GitHub Actions)
- 4 مزودي ذكاء مع fallback تلقائي

## التشغيل المحلي

    pip install -r requirements.txt
    cp .env.example .env
    uvicorn app.main:app --reload --port 8000

## النشر على Render

1. ارفع المشروع إلى GitHub
2. Render -> New Web Service -> اختر الريبو
3. Build Command: pip install -r requirements.txt
4. Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT

## المسارات

- /          شاشة الاختيار
- /creative  الواجهة الإبداعية
- /studio    الاستوديو
- /gallery   المعرض
- /admin     الإدارة
- /docs      توثيق API
