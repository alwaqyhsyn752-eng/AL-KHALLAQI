#!/usr/bin/env python3
from pathlib import Path

BASE = Path(__file__).resolve().parent
wf = BASE / ".github" / "workflows" / "build-apk.yml"
src = wf.read_text(encoding="utf-8")

# 1) أضف permissions بعد اسم الـ workflow
if "permissions:" not in src:
    src = src.replace(
        "on:\n  workflow_dispatch:",
        "permissions:\n  contents: write\n\non:\n  workflow_dispatch:"
    )
    print("[+] أضفت permissions")

# 2) اجعل خطوة Release "غير مطلوبة" حتى لو فشلت
src = src.replace(
    "      - name: Create Release\n        if: github.event_name == 'workflow_dispatch'",
    "      - name: Create Release\n        if: github.event_name == 'workflow_dispatch'\n        continue-on-error: true"
)
print("[+] Release لن يفشل البناء")

wf.write_text(src, encoding="utf-8")
print()
print("=" * 60)
print("  الحل:")
print("  ✓ permissions: contents: write")
print("  ✓ Release لن يوقف البناء إن فشل")
print("=" * 60)
print()
print("ارفع:")
print("   git add -A")
print("   git commit -m 'Fix release permissions'")
print("   git push origin main")
