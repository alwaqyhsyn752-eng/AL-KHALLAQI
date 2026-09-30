#!/usr/bin/env python3
from pathlib import Path

main = Path("app/main.py")
s = main.read_text(encoding="utf-8")

# 1) استبدل دالة _render بنسخة فيها fallback HTML مدمج
OLD_RENDER_START = "def _render(name: str, request: Request, **kw):"
idx = s.find(OLD_RENDER_START)
if idx == -1:
    print("❌ لم أجد _render")
    raise SystemExit(1)

# ابحث عن نهاية الدالة (أول @app.get بعدها)
end_marker = '@app.get("/", response_class=HTMLResponse)'
end_idx = s.find(end_marker, idx)
if end_idx == -1:
    print("❌ لم أجد نهاية _render")
    raise SystemExit(1)

NEW_RENDER = '''FALLBACK_HTML = """<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Poppins',system-ui,sans-serif;background:#05030f;color:#f5f3ff;
min-height:100vh;overflow-x:hidden;position:relative}
body::before{content:"";position:fixed;inset:-20%;z-index:-2;
background:radial-gradient(circle at 20% 20%,rgba(168,85,247,.35),transparent 45%),
radial-gradient(circle at 80% 30%,rgba(34,211,238,.3),transparent 45%),
radial-gradient(circle at 50% 80%,rgba(244,114,182,.25),transparent 50%);
filter:blur(60px);animation:aurora 18s ease-in-out infinite alternate}
@keyframes aurora{0%{transform:translate(0,0) scale(1)}
50%{transform:translate(3%,-2%) scale(1.08)}100%{transform:translate(-2%,2%) scale(1.02)}}
.hero{text-align:center;padding:80px 20px 30px}
h1{font-size:clamp(38px,8vw,90px);font-weight:900;letter-spacing:4px;
background:linear-gradient(90deg,#a855f7,#22d3ee,#fbbf24,#f472b6);
background-size:300% 100%;-webkit-background-clip:text;background-clip:text;
color:transparent;animation:shine 5s linear infinite}
@keyframes shine{0%{background-position:0% 50%}100%{background-position:300% 50%}}
p{margin-top:14px;color:#c4b5fd;font-size:18px}
.cards{max-width:1100px;margin:40px auto;padding:0 20px;display:grid;
gap:20px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.card{padding:26px;border-radius:22px;text-decoration:none;color:#f5f3ff;
background:rgba(30,27,75,.45);backdrop-filter:blur(18px);
border:1px solid rgba(168,85,247,.35);
transition:transform .3s cubic-bezier(.2,.8,.2,1),box-shadow .3s}
.card:hover{transform:translateY(-6px);box-shadow:0 16px 50px rgba(168,85,247,.4)}
.icon{font-size:34px;margin-bottom:12px}
h3{font-size:20px;margin-bottom:6px}
.card p{color:#c4b5fd;font-size:14px;line-height:1.6}
.chip{display:inline-block;padding:5px 12px;border-radius:999px;
background:rgba(168,85,247,.15);border:1px solid rgba(168,85,247,.35);
color:#c4b5fd;font-size:12px;margin:4px}
.topbar{padding:14px 20px;display:flex;justify-content:space-between;
align-items:center;background:rgba(5,3,15,.65);backdrop-filter:blur(16px);
border-bottom:1px solid rgba(168,85,247,.35);position:sticky;top:0;z-index:20}
.brand{font-weight:900;font-size:20px;letter-spacing:1px;
background:linear-gradient(90deg,#a855f7,#22d3ee,#fbbf24,#f472b6);
background-size:300% 100%;-webkit-background-clip:text;background-clip:text;
color:transparent;animation:shine 6s linear infinite}
</style></head>
<body>
<div class="topbar"><span class="brand">AL-KHALLAQI</span>
<span class="chip">الإبداع بلا حدود</span></div>
<div class="hero"><h1>AL-KHALLAQI</h1>
<p>وكيل الذكاء الاصطناعي الإبداعي — طوّره Hussein Ghallab</p></div>
<div class="cards">
<a class="card" href="/creative"><div class="icon">✨</div><h3>الواجهة الإبداعية</h3><p>تحدّث مع الوكيل الذكي.</p></a>
<a class="card" href="/studio"><div class="icon">🎨</div><h3>استوديو الإبداع</h3><p>صور، فيديو، نصوص، شعارات.</p></a>
<a class="card" href="/gallery"><div class="icon">🖼️</div><h3>معرض الأعمال</h3><p>تصفّح أعمالك.</p></a>
<a class="card" href="/admin"><div class="icon">⚙️</div><h3>لوحة الإدارة</h3><p>إحصائيات النظام.</p></a>
<a class="card" href="/docs"><div class="icon">📚</div><h3>توثيق API</h3><p>المسارات التفاعلية.</p></a>
<a class="card" href="/api/v1/health"><div class="icon">💚</div><h3>الحالة</h3><p>صحة النظام.</p></a>
</div>
</body></html>"""


def _render(name: str, request: Request, **kw):
    # 1) جرّب Jinja2 أولاً
    try:
        if TEMPLATES_DIR.exists() and (TEMPLATES_DIR / name).exists():
            return templates.TemplateResponse(
                name, {"request": request, "settings": settings, **kw})
    except Exception as e:
        log.warning("jinja render failed for %s: %s", name, e)

    # 2) fallback: قالب مدمج (يعمل دائماً)
    if name == "choice.html":
        return HTMLResponse(FALLBACK_HTML)

    # 3) أي قالب آخر: رد مبسط
    return HTMLResponse(
        f"<html><body style='background:#05030f;color:#f5f3ff;"
        f"font-family:sans-serif;padding:40px;text-align:center'>"
        f"<h1>{settings.APP_NAME}</h1><p>هذه الصفحة ({name}) "
        f"تحتاج إلى قوالب. عرض الحالة: "
        f"<a style='color:#22d3ee' href='/'>العودة للرئيسية</a></p></body></html>")


'''

s = s[:idx] + NEW_RENDER + s[end_idx:]
main.write_text(s, encoding="utf-8")
print("✅ تم تحديث main.py بالقالب المدمج")
