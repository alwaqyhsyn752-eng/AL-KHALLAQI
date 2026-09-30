#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AL-KHALLAQI — Auto Fix & Push
يُصلح مسارات القوالب + يتأكد من الملفات + يرفع على GitHub
تشغيل: python fix_and_push.py
"""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
os_repo = "https://github.com/alwaqyhsyn752-eng/al-khallaqi.git"


def run(cmd, check=False):
    print(f"$ {cmd}")
    r = subprocess.run(cmd, shell=True, cwd=BASE,
                       capture_output=True, text=True)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.stderr:
        print(r.stderr.rstrip())
    if check and r.returncode != 0:
        print(f"❌ فشل: {cmd}")
        sys.exit(1)
    return r


def step(n, title):
    print("\n" + "=" * 62)
    print(f"الخطوة {n}: {title}")
    print("=" * 62)


# ─────────────────────────────────────────────────────────────
step(1, "فحص البنية")
required = ["app", "templates", "static", "requirements.txt"]
missing = [d for d in required if not (BASE / d).exists()]
if missing:
    print(f"❌ مفقود: {missing}")
    print("شغّل أولاً: python install_al_khallaqi.py")
    sys.exit(1)
print("✅ كل المجلدات موجودة")

# ─────────────────────────────────────────────────────────────
step(2, "فحص القوالب")
tpl = BASE / "templates"
tmpls = sorted(p.name for p in tpl.glob("*.html"))
print(f"📁 templates: {len(tmpls)} ملف")
for t in tmpls:
    print(f"   - {t}")

needed = ["choice.html", "creative.html", "studio.html",
          "gallery.html", "work_view.html", "admin.html"]
for n in needed:
    if not (tpl / n).exists():
        print(f"⚠️  ناقص: {n}")

# ─────────────────────────────────────────────────────────────
step(3, "إصلاح main.py — مسارات مرنة")

main_path = BASE / "app" / "main.py"
src = main_path.read_text(encoding="utf-8")

OLD = '''BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)'''

NEW = '''_HERE = Path(__file__).resolve()
_CANDIDATES = [
    _HERE.parent.parent,
    _HERE.parent,
    Path.cwd(),
]

def _find_dir(name: str) -> Path:
    for base in _CANDIDATES:
        d = base / name
        if d.is_dir() and any(d.iterdir()) if d.exists() else False:
            return d
    for base in _CANDIDATES:
        d = base / name
        if d.is_dir():
            return d
    d = _HERE.parent.parent / name
    d.mkdir(parents=True, exist_ok=True)
    return d

TEMPLATES_DIR = _find_dir("templates")
STATIC_DIR = _find_dir("static")
STATIC_DIR.mkdir(exist_ok=True)

# Debug: طباعة المسارات الفعلية
import sys as _sys
print(f"[AL-KHALLAQI] TEMPLATES_DIR = {TEMPLATES_DIR}", file=_sys.stderr)
print(f"[AL-KHALLAQI] STATIC_DIR    = {STATIC_DIR}", file=_sys.stderr)
print(f"[AL-KHALLAQI] exists: {TEMPLATES_DIR.exists()}", file=_sys.stderr)
if TEMPLATES_DIR.exists():
    print(f"[AL-KHALLAQI] files: {[p.name for p in TEMPLATES_DIR.iterdir()]}", file=_sys.stderr)'''

if OLD in src:
    src = src.replace(OLD, NEW)
    main_path.write_text(src, encoding="utf-8")
    print("✅ تم إصلاح main.py")
elif "_find_dir" in src:
    print("ℹ️  main.py مُصلَح مسبقاً")
else:
    print("⚠️  لم أجد الكتلة الأصلية — سأتخطاها")
    print("   افتح app/main.py يدوياً وتحقق من السطور 20-25")

# ─────────────────────────────────────────────────────────────
step(4, "تهيئة Git")

run('git config user.name "Hussein Ghallab"')
run('git config user.email "alwaqyhsyn752-eng@users.noreply.github.com"')

# تأكد من الفرع
r = run("git rev-parse --abbrev-ref HEAD")
if "main" not in r.stdout:
    run("git branch -M main")

# تأكد من remote
r = run("git remote -v")
if "origin" not in r.stdout:
    run(f"git remote add origin {os_repo}")
    print("✅ أضفت remote")
else:
    run(f"git remote set-url origin {os_repo}")
    print("✅ حدّثت remote")

# ─────────────────────────────────────────────────────────────
step(5, "إضافة وتثبيت")

run("git add -A")

r = run("git status --short")
if not r.stdout.strip():
    print("⚠️  لا يوجد تغييرات جديدة — كل شيء مرفوع")
else:
    print(r.stdout)

# ─────────────────────────────────────────────────────────────
step(6, "إنشاء commit")

r = run('git commit -m "AL-KHALLAQI: auto-fix templates path + full structure"')
if "nothing to commit" in (r.stdout + r.stderr).lower():
    print("ℹ️  لا يوجد commit جديد")
else:
    print("✅ تم الإنشاء")

# ─────────────────────────────────────────────────────────────
step(7, "التحقق من الملفات المتعقّبة")
r = run("git ls-files templates/")
tpl_count = len([l for l in r.stdout.splitlines() if l.strip()])
print(f"📦 عدد القوالب المتعقّبة: {tpl_count}")

if tpl_count == 0:
    print("❌ القوالب غير مضافة! تحقق من .gitignore")
    print("   شغّل: cat .gitignore")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────
step(8, "الرفع على GitHub")
print("⚠️  سيطلب Username و Password (استخدم Personal Access Token)")
print("   Username: alwaqyhsyn752-eng")
print("   Password: <التوكن من github.com/settings/tokens>")
print()
r = run("git push -u origin main")

if r.returncode == 0:
    print("\n" + "🎉" * 20)
    print("✅ تم الرفع بنجاح!")
    print(f"   https://github.com/alwaqyhsyn752-eng/al-khallaqi")
    print("\n📌 الخطوة التالية:")
    print("   1) افتح https://dashboard.render.com")
    print("   2) اختر خدمة al-khallaqi")
    print("   3) اضغط Manual Deploy → Deploy latest commit")
    print("🎉" * 20)
else:
    print("\n❌ فشل الرفع")
    print("تحقق من:")
    print("  - أنك تستخدم Personal Access Token (ليس كلمة المرور)")
    print("  - أن المستودع فارغ أو أنك تملك صلاحية الكتابة")
