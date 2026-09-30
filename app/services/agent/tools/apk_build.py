from app.services.agent.tools.registry import register


async def _run(name: str, description: str = "", html: str = ""):
    return {
        "name": name, "status": "queued",
        "note": "APK build queued. GitHub Actions workflow required.",
        "html_len": len(html),
    }


register("apk_build", "بناء تطبيق APK.", _run)
