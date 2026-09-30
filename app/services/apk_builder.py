"""APK builder via GitHub Actions."""
import base64
import httpx
from app.core.config import settings
from app.core.logging import log


async def build_apk(name: str, html: str, app_name: str = "AL-KHALLAQI") -> dict:
    """يرسل طلب بناء APK إلى GitHub Actions."""
    token = settings.GITHUB_ACTIONS_TOKEN
    if not token:
        return {"ok": False, "error": "GITHUB_ACTIONS_TOKEN غير مضبوط",
                "hint": "أضفه من Render → Environment"}

    # طريقة بديلة: Buildozer محلي (غير مدعوم على Render)
    # هنا نرسل webhook لـ GitHub Action جاهز
    return {
        "ok": False,
        "error": "بناء APK يحتاج إعداد GitHub Actions",
        "instructions": [
            "1. أضف ملف .github/workflows/build-apk.yml",
            "2. شغّل الـ workflow يدوياً من GitHub",
            "3. حمّل APK من صفحة Actions",
        ],
    }
