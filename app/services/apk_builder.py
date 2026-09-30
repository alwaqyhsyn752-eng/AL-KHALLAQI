"""APK Builder via GitHub Actions API."""
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
