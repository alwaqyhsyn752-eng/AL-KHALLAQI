#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AL-KHALLAQI — APK Builder (Capacitor) + Gemini optimizations."""
from pathlib import Path

BASE = Path(__file__).resolve().parent

def w(rel, content):
    p = BASE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"[+] {rel}")

# ═══════════════════════════════════════════════════════════
# 1) Capacitor mobile project
# ═══════════════════════════════════════════════════════════
w("mobile/package.json", """{
  "name": "al-khallaqi",
  "version": "1.0.0",
  "description": "AL-KHALLAQI Creative AI Agent",
  "scripts": {
    "build": "echo 'no build needed'"
  },
  "dependencies": {
    "@capacitor/android": "^6.1.2",
    "@capacitor/core": "^6.1.2"
  },
  "devDependencies": {
    "@capacitor/cli": "^6.1.2"
  }
}
""")

w("mobile/capacitor.config.json", """{
  "appId": "com.hussein.alkhallaqi",
  "appName": "AL-KHALLAQI",
  "webDir": "www",
  "bundledWebRuntime": false,
  "server": {
    "url": "https://al-khallaqi.onrender.com",
    "cleartext": false,
    "androidScheme": "https"
  },
  "android": {
    "allowMixedContent": true,
    "backgroundColor": "#05030f"
  }
}
""")

w("mobile/www/index.html", """<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"/>
<title>AL-KHALLAQI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#05030f;color:#f5f3ff;font-family:sans-serif;
  height:100vh;display:flex;align-items:center;justify-content:center;
  flex-direction:column;gap:20px;overflow:hidden}
.logo{font-size:42px;font-weight:800;letter-spacing:4px;
  background:linear-gradient(90deg,#a855f7,#22d3ee,#fbbf24,#f472b6);
  background-size:300% 100%;-webkit-background-clip:text;background-clip:text;
  color:transparent;animation:shine 3s linear infinite}
@keyframes shine{0%{background-position:0% 50%}100%{background-position:300% 50%}}
.sub{color:#c4b5fd;font-size:14px}
.loader{width:40px;height:40px;border:3px solid rgba(168,85,247,.3);
  border-top-color:#a855f7;border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="logo">AL-KHALLAQI</div>
<div class="sub">جارٍ التحميل...</div>
<div class="loader"></div>
<script>
// يحمّل الموقع الرئيسي
window.location.replace('https://al-khallaqi.onrender.com');
</script>
</body>
</html>
""")

# ═══════════════════════════════════════════════════════════
# 2) GitHub Actions workflow
# ═══════════════════════════════════════════════════════════
w(".github/workflows/build-apk.yml", """name: Build AL-KHALLAQI APK

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version name'
        required: false
        default: '1.0.0'
  push:
    branches: [main]
    paths:
      - 'mobile/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Setup Java 17
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Setup Android SDK
        uses: android-actions/setup-android@v3

      - name: Install Capacitor CLI
        working-directory: mobile
        run: |
          npm install
          npx cap add android || true

      - name: Prepare Android
        working-directory: mobile
        run: |
          npx cap sync android

      - name: Set version
        working-directory: mobile/android
        run: |
          VERSION="${{ github.event.inputs.version }}"
          VERSION="${VERSION:-1.0.0}"
          sed -i "s/versionName \\".*\\"/versionName \\"$VERSION\\"/" app/build.gradle
          echo "Building version $VERSION"

      - name: Build Debug APK
        working-directory: mobile/android
        run: |
          chmod +x gradlew
          ./gradlew assembleDebug --no-daemon

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: al-khallaqi-apk
          path: mobile/android/app/build/outputs/apk/debug/*.apk
          retention-days: 30

      - name: Release APK
        if: github.event_name == 'workflow_dispatch'
        uses: softprops/action-gh-release@v2
        with:
          tag_name: v${{ github.event.inputs.version }}
          name: AL-KHALLAQI v${{ github.event.inputs.version }}
          files: mobile/android/app/build/outputs/apk/debug/*.apk
          draft: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
""")

# ═══════════════════════════════════════════════════════════
# 3) APK Builder service — يستدعي GitHub API
# ═══════════════════════════════════════════════════════════
w("app/services/apk_builder.py", r'''"""APK Builder via GitHub Actions API."""
from typing import Optional
import httpx
from app.core.config import settings
from app.core.logging import log


OWNER = "alwaqyhsyn752-eng"
REPO = "AL-KHALLAQI"
WORKFLOW = "build-apk.yml"


async def trigger_build(version: str = "1.0.0") -> dict:
    """يستدعي GitHub Actions workflow_dispatch."""
    token = settings.GITHUB_ACTIONS_TOKEN
    if not token:
        return {
            "ok": False,
            "error": "GITHUB_ACTIONS_TOKEN غير مضبوط",
            "how_to_fix": [
                "1. افتح https://github.com/settings/tokens",
                "2. Generate new token (classic)",
                "3. اختر: repo + workflow",
                "4. انسخ التوكن",
                "5. في Render → Environment: GITHUB_ACTIONS_TOKEN=<التوكن>",
            ],
        }

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW}/dispatches"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "ref": "main",
        "inputs": {"version": version},
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as c:
            r = await c.post(url, json=payload, headers=headers)
        if r.status_code == 204:
            return {
                "ok": True,
                "message": "بدأ البناء",
                "version": version,
                "actions_url": f"https://github.com/{OWNER}/{REPO}/actions",
                "watch_url": f"https://github.com/{OWNER}/{REPO}/actions/workflows/{WORKFLOW}",
                "note": "سيستغرق 5-10 دقائق. حمّل APK من صفحة Actions.",
            }
        return {
            "ok": False,
            "error": f"GitHub API: {r.status_code}",
            "detail": r.text[:300],
        }
    except Exception as e:
        log.error("trigger_build failed: %s", e)
        return {"ok": False, "error": str(e)}


async def get_latest_release() -> dict:
    """يعيد أحدث release فيه APK."""
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"
    try:
        async with httpx.AsyncClient(timeout=20.0) as c:
            r = await c.get(url)
        if r.status_code != 200:
            return {"ok": False, "error": f"{r.status_code}"}
        data = r.json()
        apk = None
        for asset in data.get("assets", []):
            if asset["name"].endswith(".apk"):
                apk = asset["browser_download_url"]
                break
        return {
            "ok": True,
            "tag": data.get("tag_name"),
            "name": data.get("name"),
            "apk_url": apk,
            "published": data.get("published_at"),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
''')

# ═══════════════════════════════════════════════════════════
# 4) APK endpoint
# ═══════════════════════════════════════════════════════════
w("app/api/v1/endpoints/apk.py", r'''"""APK builder endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel
from app.services import apk_builder

router = APIRouter()


class BuildRequest(BaseModel):
    version: str = "1.0.0"


@router.post("/build")
async def build(req: BuildRequest):
    return await apk_builder.trigger_build(req.version)


@router.get("/latest")
async def latest():
    return await apk_builder.get_latest_release()
''')

# تحديث router الرئيسي
router_path = BASE / "app" / "api" / "v1" / "router.py"
src = router_path.read_text(encoding="utf-8")
if "apk" not in src:
    src = src.replace(
        "    system, creative, studio, agent, chat, gallery, admin, apikeys,",
        "    system, creative, studio, agent, chat, gallery, admin, apikeys, apk,"
    )
    src = src.replace(
        'api.include_router(apikeys.router, prefix="/apikeys", tags=["apikeys"])',
        'api.include_router(apikeys.router, prefix="/apikeys", tags=["apikeys"])\n'
        'api.include_router(apk.router, prefix="/apk", tags=["apk"])'
    )
    router_path.write_text(src, encoding="utf-8")
    print("[+] app/api/v1/router.py (apk included)")

# ═══════════════════════════════════════════════════════════
# 5) Gemini — إضافة مفتاح احتياطي + تحسين
# ═══════════════════════════════════════════════════════════
GEMINI_PATCH = r'''"""Gemini — مجاني مع مفتاح احتياطي + نماذج متعددة."""
from typing import List, Optional
import httpx
from app.core.config import settings
from app.core.exceptions import ProviderError
from app.core.logging import log
from app.services.ai.base import BaseProvider, ChatMessage


# أحدث النماذج المجانية (من Google AI Studio)
TEXT_MODELS = [
    "gemini-2.5-flash",              # مجاني، سريع
    "gemini-2.5-pro",                # مجاني بحصة أعلى
    "gemini-2.0-flash",              # مجاني مستقر
    "gemini-2.0-flash-exp",          # تجريبي
    "gemini-1.5-flash-latest",       # احتياطي
    "gemini-1.5-pro-latest",         # احتياطي
]

BASE_V1BETA = "https://generativelanguage.googleapis.com/v1beta"


class GeminiProvider(BaseProvider):
    name = "gemini"
    default_model = "gemini-2.5-flash"

    @property
    def keys(self) -> list:
        """قائمة المفاتيح — يدعم مفتاحين للتبديل عند نفاد الحصة."""
        keys = []
        k1 = getattr(settings, "GEMINI_API_KEY", "")
        k2 = getattr(settings, "GEMINI_API_KEY_FALLBACK", "")
        if k1: keys.append(k1)
        if k2: keys.append(k2)
        return keys

    async def chat(self, messages: List[ChatMessage],
                   system: Optional[str] = None,
                   temperature: float = 0.8,
                   max_tokens: int = 2048,
                   model: Optional[str] = None) -> str:
        if not self.keys:
            raise ProviderError("gemini: no API key")

        contents = []
        for m in messages:
            role = "user" if m.role in ("user", "system") else "model"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        body = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}

        candidates = [model] if model else TEXT_MODELS
        last_err = None

        # جرّب كل مفتاح × كل نموذج
        for key in self.keys:
            for mdl in candidates:
                url = f"{BASE_V1BETA}/models/{mdl}:generateContent"
                try:
                    async with httpx.AsyncClient(timeout=90.0) as c:
                        r = await c.post(
                            url, json=body,
                            headers={"x-goog-api-key": key,
                                     "Content-Type": "application/json"},
                        )
                    if r.status_code == 429:
                        last_err = f"{mdl}: 429 (quota)"
                        continue  # جرّب المفتاح/النموذج التالي
                    if r.status_code == 404:
                        last_err = f"{mdl}: 404"
                        continue
                    if r.status_code >= 400:
                        last_err = f"{mdl}: {r.status_code}"
                        continue
                    data = r.json()
                    log.info("gemini OK: %s (key %s...)", mdl, key[:6])
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except Exception as e:
                    last_err = f"{mdl}: {e}"
                    continue

        raise ProviderError(f"gemini: {last_err}")
'''

w("app/services/ai/gemini.py", GEMINI_PATCH)

# إضافة GEMINI_API_KEY_FALLBACK للـ config
cfg_path = BASE / "app" / "core" / "config.py"
src = cfg_path.read_text(encoding="utf-8")
if "GEMINI_API_KEY_FALLBACK" not in src:
    src = src.replace(
        'GEMINI_API_KEY: str = ""',
        'GEMINI_API_KEY: str = ""\n'
        '    GEMINI_API_KEY_FALLBACK: str = ""'
    )
    cfg_path.write_text(src, encoding="utf-8")
    print("[+] app/core/config.py (Gemini fallback key)")

# ═══════════════════════════════════════════════════════════
# 6) صفحة APK في الواجهة
# ═══════════════════════════════════════════════════════════
w("templates/apk.html", r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — APK</title>
<link rel="stylesheet" href="/static/css/main.css">
<style>
.wrap{max-width:700px;margin:0 auto;padding:30px}
.status{padding:20px;border-radius:16px;background:var(--card);
  border:1px solid var(--border);margin-bottom:20px}
.status .label{color:var(--muted);font-size:13px;letter-spacing:1px}
.status .value{margin-top:8px;font-size:15px;color:var(--c2)}
.url{word-break:break-all;padding:12px;border-radius:10px;
  background:rgba(0,0,0,.3);margin-top:10px;font-size:13px;
  font-family:monospace;color:var(--c2)}
.link{display:inline-block;padding:12px 24px;border-radius:12px;
  background:linear-gradient(135deg,var(--c1),var(--c5));
  color:#fff;text-decoration:none;font-weight:700;margin:10px 5px;
  box-shadow:0 6px 24px rgba(168,85,247,.4)}
h2{color:var(--c1);margin-bottom:20px;letter-spacing:1px}
</style>
</head>
<body>
<div class="topbar">
  <span class="brand">AL-KHALLAQI</span>
  <span class="chip">APK</span>
</div>
<div class="wrap">
  <h2>بناء تطبيق APK</h2>

  <div class="status">
    <div class="label">الإصدار</div>
    <div class="value"><input class="input" id="ver" value="1.0.0" style="max-width:150px;display:inline-block"></div>
  </div>

  <button class="btn" onclick="build()" style="width:100%;padding:16px;font-size:16px">
    ابدأ البناء
  </button>

  <div id="result" style="margin-top:20px"></div>

  <div style="margin-top:30px">
    <div class="status">
      <div class="label">المرجع</div>
      <div class="value">صفحة البناء على GitHub</div>
      <a class="link" target="_blank"
        href="https://github.com/alwaqyhsyn752-eng/AL-KHALLAQI/actions/workflows/build-apk.yml">
        فتح Actions
      </a>
      <a class="link" target="_blank"
        href="https://github.com/alwaqyhsyn752-eng/AL-KHALLAQI/releases">
        تحميل Releases
      </a>
    </div>
  </div>
</div>
<script>
async function build(){
  const v=document.getElementById('ver').value||'1.0.0';
  const out=document.getElementById('result');
  out.innerHTML='<div class="status"><div class="value pulse">جارٍ الإرسال...</div></div>';
  try{
    const r=await fetch('/api/v1/apk/build',{method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({version:v})});
    const d=await r.json();
    if(d.ok){
      out.innerHTML='<div class="status">'
        +'<div class="label">الحالة</div>'
        +'<div class="value">بدأ البناء</div>'
        +'<div class="url">'+d.actions_url+'</div>'
        +'<p style="margin-top:10px;color:var(--muted)">'+d.note+'</p>'
        +'</div>';
    }else{
      let html='<div class="status" style="border-color:#f87171">'
        +'<div class="label">خطأ</div>'
        +'<div class="value" style="color:#f87171">'+(d.error||'فشل')+'</div>';
      if(d.how_to_fix){
        html+='<ul style="margin-top:10px;padding-inline-start:20px;color:var(--muted)">';
        d.how_to_fix.forEach(s=>html+='<li>'+s+'</li>');
        html+='</ul>';
      }
      html+='</div>';
      out.innerHTML=html;
    }
  }catch(e){
    out.innerHTML='<div class="status" style="border-color:#f87171">'
      +'<div class="value" style="color:#f87171">خطأ: '+e.message+'</div></div>';
  }
}
</script>
</body>
</html>
''')

# إضافة route للـ APK page
main_path = BASE / "app" / "main.py"
src = main_path.read_text(encoding="utf-8")
if '@app.get("/apk"' not in src:
    addition = '''

@app.get("/apk", response_class=HTMLResponse)
async def apk_page(request: Request):
    return _render("apk.html", request)
'''
    src = src.rstrip() + addition
    main_path.write_text(src, encoding="utf-8")
    print("[+] app/main.py (/apk route)")

# إضافة بطاقة APK في choice.html
choice_path = BASE / "templates" / "choice.html"
src = choice_path.read_text(encoding="utf-8")
if '/apk' not in src:
    src = src.replace(
        '''  <a class="card" href="/docs">''',
        '''  <a class="card" href="/apk">
    <div class="icon">&#9635; <span class="num">05</span></div>
    <h3>بناء APK</h3>
    <p>حوّل المشروع إلى تطبيق أندرويد جاهز.</p>
  </a>
  <a class="card" href="/docs">'''
    )
    choice_path.write_text(src, encoding="utf-8")
    print("[+] templates/choice.html (APK card)")

print()
print("=" * 60)
print("  اكتمل التحديث")
print("=" * 60)
print()
print("  ما تم:")
print("  ✓ Capacitor project (mobile/)")
print("  ✓ GitHub Actions workflow (build-apk.yml)")
print("  ✓ APK endpoints (/api/v1/apk/build)")
print("  ✓ صفحة APK (/apk)")
print("  ✓ Gemini: مفتاحان + 6 نماذج")
print()
print("ارفع الآن:")
print("   git add -A")
print('   git commit -m "Add APK builder + Gemini dual keys"')
print("   git push origin main")
print("=" * 60)
