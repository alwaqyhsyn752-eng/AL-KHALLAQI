#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""إصلاح كل الصفحات + رموز مستقبلية (بدون إيموجي)."""
from pathlib import Path

BASE = Path(__file__).resolve().parent

def w(rel, content):
    p = BASE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"[+] {rel}")

# ═══════════════════════════════════════════════════════════
# studio.html — رموز مستقبلية
# ═══════════════════════════════════════════════════════════
STUDIO = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — الاستوديو</title>
<link rel="stylesheet" href="/static/css/main.css">
<style>
.wrap{max-width:1100px;margin:0 auto;padding:22px}
.tabs{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:22px}
.tab{padding:11px 20px;border-radius:12px;border:1px solid var(--border);
  background:rgba(11,8,32,0.6);color:var(--muted);cursor:pointer;
  font-weight:600;font-family:inherit;font-size:14px;transition:.25s}
.tab.active{background:linear-gradient(135deg,var(--c1),var(--c5));
  color:#fff;border-color:transparent;
  box-shadow:0 0 25px rgba(168,85,247,0.5)}
.panel{display:none;padding:26px}
.panel.active{display:block}
.row{display:grid;gap:12px;grid-template-columns:1fr 1fr;margin-bottom:14px}
.row.full{grid-template-columns:1fr}
.preview{margin-top:22px;min-height:200px;padding:18px;
  border-radius:16px;background:rgba(11,8,32,0.6);
  border:1px dashed var(--border)}
.preview img,.preview svg{max-width:100%;border-radius:12px}
h3{color:var(--c1);font-weight:700;letter-spacing:.5px;
  display:flex;align-items:center;gap:10px}
h3 .sym{color:var(--c2);font-size:22px}
</style>
</head>
<body>
<div class="topbar">
  <span class="brand">AL-KHALLAQI</span>
  <span class="chip">الاستوديو</span>
</div>
<div class="wrap">
  <div class="tabs">
    <button class="tab active" data-p="images">&#x2B22; صور</button>
    <button class="tab" data-p="video">&#x27C1; فيديو</button>
    <button class="tab" data-p="text">&#x25C8; نصوص</button>
    <button class="tab" data-p="identity">&#x29CA; هويات</button>
  </div>

  <div class="glass panel active" id="images">
    <h3><span class="sym">&#x2B22;</span> توليد صورة</h3><br>
    <div class="row full"><textarea class="input" id="imgPrompt" rows="3"
      placeholder="صف الصورة..."></textarea></div>
    <div class="row">
      <select class="input" id="imgStyle">
        <option value="realistic">واقعي</option>
        <option value="artistic">فني</option>
        <option value="cyberpunk">سايبربانك</option>
        <option value="anime">أنمي</option>
      </select>
      <select class="input" id="imgSize">
        <option value="1024x1024">1024x1024</option>
        <option value="768x768">768x768</option>
        <option value="1344x768">1344x768</option>
        <option value="768x1344">768x1344</option>
      </select>
    </div>
    <button class="btn" onclick="genImage()">توليد</button>
    <div class="preview" id="imgPrev">النتيجة ستظهر هنا</div>
  </div>

  <div class="glass panel" id="video">
    <h3><span class="sym">&#x27C1;</span> توليد فيديو</h3><br>
    <div class="row full"><textarea class="input" id="vidPrompt" rows="3"
      placeholder="صف الفيديو..."></textarea></div>
    <div class="row">
      <select class="input" id="vidAspect">
        <option value="16:9">16:9</option>
        <option value="9:16">9:16</option>
        <option value="1:1">1:1</option>
      </select>
      <input class="input" id="vidDur" type="number" value="4"
        min="2" max="10">
    </div>
    <button class="btn" onclick="genVideo()">توليد</button>
    <div class="preview" id="vidPrev">النتيجة ستظهر هنا</div>
  </div>

  <div class="glass panel" id="text">
    <h3><span class="sym">&#x25C8;</span> توليد نص</h3><br>
    <div class="row full"><textarea class="input" id="txtPrompt" rows="3"
      placeholder="الموضوع..."></textarea></div>
    <div class="row">
      <select class="input" id="txtKind">
        <option value="article">مقال</option>
        <option value="story">قصة</option>
        <option value="script">سيناريو</option>
      </select>
      <select class="input" id="txtTone">
        <option value="creative">إبداعي</option>
        <option value="formal">رسمي</option>
        <option value="fun">مرح</option>
      </select>
    </div>
    <button class="btn" onclick="genText()">توليد</button>
    <div class="preview" id="txtPrev">النتيجة ستظهر هنا</div>
  </div>

  <div class="glass panel" id="identity">
    <h3><span class="sym">&#x29CA;</span> بناء هوية بصرية</h3><br>
    <div class="row">
      <input class="input" id="idBrand" placeholder="اسم العلامة التجارية">
      <input class="input" id="idIndustry" placeholder="المجال (اختياري)">
    </div>
    <button class="btn" onclick="genIdentity()">بناء</button>
    <div class="preview" id="idPrev">النتيجة ستظهر هنا</div>
  </div>
</div>
<script>
document.querySelectorAll('.tab').forEach(t=>{
  t.addEventListener('click',()=>{
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(x=>x.classList.remove('active'));
    t.classList.add('active');
    document.getElementById(t.dataset.p).classList.add('active');
  });
});
async function post(path,body){
  const r=await fetch('/api/v1'+path,{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(body)});
  if(!r.ok) throw new Error(await r.text());
  return r.json();
}
async function genImage(){
  const p=document.getElementById('imgPrompt').value.trim();if(!p)return;
  const s=document.getElementById('imgStyle').value;
  const [w,h]=document.getElementById('imgSize').value.split('x').map(Number);
  const prev=document.getElementById('imgPrev');
  prev.textContent='جارٍ التوليد...';
  try{
    const d=await post('/creative/image',{prompt:p,style:s,width:w,height:h});
    prev.innerHTML='<img src="'+d.url+'"/>';
  }catch(e){prev.textContent='خطأ: '+e.message;}
}
async function genVideo(){
  const p=document.getElementById('vidPrompt').value.trim();if(!p)return;
  const prev=document.getElementById('vidPrev');
  prev.textContent='جارٍ التوليد...';
  try{
    const d=await post('/creative/video',{prompt:p,
      aspect:document.getElementById('vidAspect').value,
      duration:Number(document.getElementById('vidDur').value)||4});
    if(d.gif){prev.innerHTML='<img src="'+d.gif+'"/>';}
    else{prev.innerHTML=d.frames.map(u=>
      '<img style="max-width:180px;margin:4px" src="'+u+'"/>').join('');}
  }catch(e){prev.textContent='خطأ: '+e.message;}
}
async function genText(){
  const p=document.getElementById('txtPrompt').value.trim();if(!p)return;
  const prev=document.getElementById('txtPrev');
  prev.textContent='جارٍ الكتابة...';
  try{
    const d=await post('/creative/text',{prompt:p,
      kind:document.getElementById('txtKind').value,
      tone:document.getElementById('txtTone').value});
    prev.innerHTML=d.text.replace(/\n/g,'<br>');
  }catch(e){prev.textContent='خطأ: '+e.message;}
}
async function genIdentity(){
  const b=document.getElementById('idBrand').value.trim();if(!b)return;
  const prev=document.getElementById('idPrev');
  prev.textContent='جارٍ البناء...';
  try{
    const d=await post('/studio/identity',{brand:b,
      industry:document.getElementById('idIndustry').value});
    const pal=(d.palette||[]).map(c=>
      '<span style="display:inline-block;width:32px;height:32px;'
      +'border-radius:8px;background:'+c+';margin:3px;'
      +'box-shadow:0 0 15px '+c+'"></span>').join('');
    prev.innerHTML='<b>'+d.brand+'</b><br><i>'+(d.tagline||'')+'</i><br>'
      +'<div style="margin:10px 0">'+pal+'</div>'+(d.logo_svg||'');
  }catch(e){prev.textContent='خطأ: '+e.message;}
}
</script>
</body>
</html>
'''
w("templates/studio.html", STUDIO)

# ═══════════════════════════════════════════════════════════
# gallery.html
# ═══════════════════════════════════════════════════════════
GALLERY = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — المعرض</title>
<link rel="stylesheet" href="/static/css/main.css">
<style>
.wrap{max-width:1100px;margin:0 auto;padding:22px}
.cardwork{padding:16px;border-radius:18px;background:var(--card);
  border:1px solid var(--border);transition:.3s;cursor:pointer;
  text-decoration:none;color:inherit;display:block}
.cardwork:hover{transform:translateY(-4px);border-color:var(--c2);
  box-shadow:0 14px 45px rgba(34,211,238,0.3)}
.cardwork .kind{font-size:11px;color:var(--c2);letter-spacing:2px;
  text-transform:uppercase}
.cardwork h4{margin:10px 0 6px;color:var(--c1);font-weight:700}
.empty{padding:80px 20px;text-align:center;color:var(--muted)}
.empty .sym{color:var(--c2);font-size:32px;display:block;
  margin-bottom:14px}
</style></head>
<body>
<div class="topbar">
  <span class="brand">AL-KHALLAQI</span>
  <span class="chip">المعرض</span>
</div>
<div class="wrap">
  <h2 style="color:var(--c1);margin-bottom:20px;letter-spacing:1px">
    &#x25C8; معرض الأعمال
  </h2>
  <div class="grid g2" id="grid"></div>
  <div class="empty" id="empty" style="display:none">
    <span class="sym">&#x2B22;</span>
    لا توجد أعمال بعد. ابدأ من
    <a href="/studio" style="color:var(--c2)">الاستوديو</a>.
  </div>
</div>
<script>
(async()=>{
  try{
    const r=await fetch('/api/v1/gallery/works?limit=100');
    const d=await r.json();
    const grid=document.getElementById('grid');
    if(!d.works||!d.works.length){
      document.getElementById('empty').style.display='block';
      return;
    }
    d.works.forEach(w=>{
      const a=document.createElement('a');
      a.href='/work/'+w.id;a.className='cardwork';
      a.innerHTML='<div class="kind">'+w.kind+'</div>'
        +'<h4>'+w.title+'</h4>'
        +'<div class="muted" style="font-size:12px">'
        +(w.created_at||'').split('T')[0]+'</div>';
      grid.appendChild(a);
    });
  }catch(e){console.warn(e);}
})();
</script>
</body></html>
'''
w("templates/gallery.html", GALLERY)

# ═══════════════════════════════════════════════════════════
# work_view.html
# ═══════════════════════════════════════════════════════════
WORK_VIEW = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — عرض العمل</title>
<link rel="stylesheet" href="/static/css/main.css">
<style>
.wrap{max-width:900px;margin:0 auto;padding:26px}
.body{padding:26px;border-radius:20px;background:var(--card);
  border:1px solid var(--border)}
.body img,.body svg{max-width:100%;border-radius:14px;display:block;
  margin:14px 0;box-shadow:0 10px 40px rgba(0,0,0,0.5)}
.actions{display:flex;gap:10px;margin-top:22px}
h2{color:var(--c1);letter-spacing:1px}
</style></head>
<body>
<div class="topbar">
  <span class="brand">AL-KHALLAQI</span>
  <span class="chip">عرض عمل</span>
</div>
<div class="wrap">
  <div class="body" id="body">جارٍ التحميل...</div>
  <div class="actions" id="actions"></div>
</div>
<script>
const wid=location.pathname.split('/').pop();
(async()=>{
  try{
    const r=await fetch('/api/v1/gallery/works/'+wid);
    if(!r.ok){document.getElementById('body').textContent='غير موجود';return;}
    const w=await r.json();
    const b=document.getElementById('body');
    let html='<h2>'+w.title+'</h2>'
      +'<div class="chip" style="margin:10px 0">'+w.kind+'</div>';
    if(w.prompt) html+='<p class="muted">'+w.prompt+'</p>';
    if(w.content) html+='<div>'+w.content+'</div>';
    const ex=w.extra||{};
    if(ex.url) html+='<img src="'+ex.url+'"/>';
    if(ex.svg) html+=ex.svg;
    if(ex.text) html+='<div>'+ex.text.replace(/\n/g,'<br>')+'</div>';
    b.innerHTML=html;
    document.getElementById('actions').innerHTML=
      '<button class="btn" onclick="history.back()">رجوع &#x25B8;</button>';
  }catch(e){
    document.getElementById('body').textContent='خطأ: '+e.message;
  }
})();
</script>
</body></html>
'''
w("templates/work_view.html", WORK_VIEW)

# ═══════════════════════════════════════════════════════════
# apk.html
# ═══════════════════════════════════════════════════════════
APK = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — APK</title>
<link rel="stylesheet" href="/static/css/main.css">
<style>
.wrap{max-width:700px;margin:0 auto;padding:26px}
.section{padding:22px;border-radius:18px;background:var(--card);
  border:1px solid var(--border);margin-bottom:18px}
.section h3{color:var(--c1);margin-bottom:14px;letter-spacing:1px;
  display:flex;align-items:center;gap:10px}
.section h3 .sym{color:var(--c2);font-size:22px}
.status{padding:16px;border-radius:14px;background:rgba(11,8,32,0.7);
  border:1px solid var(--border);margin-top:14px}
.status .label{color:var(--muted);font-size:12px;letter-spacing:1px}
.status .value{margin-top:8px;font-size:15px;color:var(--c2);
  word-break:break-all}
.link{display:inline-block;padding:12px 24px;border-radius:12px;
  background:linear-gradient(135deg,var(--c1),var(--c5));
  color:#fff;text-decoration:none;font-weight:700;margin:8px 4px;
  box-shadow:0 6px 24px rgba(168,85,247,0.4)}
h2{color:var(--c1);margin-bottom:20px;letter-spacing:1px}
</style>
</head>
<body>
<div class="topbar">
  <span class="brand">AL-KHALLAQI</span>
  <span class="chip">APK</span>
</div>
<div class="wrap">
  <h2><span style="color:var(--c2)">&#x27D0;</span> بناء تطبيق APK</h2>

  <div class="section">
    <h3><span class="sym">&#x27D0;</span> الإصدار</h3>
    <input class="input" id="ver" value="1.0.0" style="max-width:180px">
  </div>

  <button class="btn" onclick="build()"
    style="width:100%;padding:16px;font-size:16px">
    ابدأ البناء
  </button>

  <div id="result" style="margin-top:20px"></div>

  <div class="section" style="margin-top:24px">
    <h3><span class="sym">&#x2B22;</span> المراجع</h3>
    <a class="link" target="_blank"
      href="https://github.com/alwaqyhsyn752-eng/AL-KHALLAQI/actions/workflows/build-apk.yml">
      GitHub Actions
    </a>
    <a class="link" target="_blank"
      href="https://github.com/alwaqyhsyn752-eng/AL-KHALLAQI/releases">
      الإصدارات
    </a>
  </div>
</div>
<script>
async function build(){
  const v=document.getElementById('ver').value||'1.0.0';
  const out=document.getElementById('result');
  out.innerHTML='<div class="status"><div class="value pulse">'
    +'جارٍ الإرسال...</div></div>';
  try{
    const r=await fetch('/api/v1/apk/build',{method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({version:v})});
    const d=await r.json();
    if(d.ok){
      out.innerHTML='<div class="status">'
        +'<div class="label">الحالة</div>'
        +'<div class="value">بدأ البناء</div>'
        +'<div class="value" style="margin-top:10px">'+d.actions_url+'</div>'
        +'<p style="margin-top:10px;color:var(--muted)">'+d.note+'</p>'
        +'</div>';
    }else{
      let html='<div class="status" style="border-color:#f87171">'
        +'<div class="label">خطأ</div>'
        +'<div class="value" style="color:#f87171">'
        +(d.error||'فشل')+'</div>';
      if(d.how_to_fix){
        html+='<ul style="margin-top:10px;padding-inline-start:20px;'
          +'color:var(--muted)">';
        d.how_to_fix.forEach(s=>html+='<li>'+s+'</li>');
        html+='</ul>';
      }
      html+='</div>';
      out.innerHTML=html;
    }
  }catch(e){
    out.innerHTML='<div class="status" style="border-color:#f87171">'
      +'<div class="value" style="color:#f87171">خطأ: '
      +e.message+'</div></div>';
  }
}
</script>
</body>
</html>
'''
w("templates/apk.html", APK)

# ═══════════════════════════════════════════════════════════
# choice.html — رموز مستقبلية
# ═══════════════════════════════════════════════════════════
CHOICE = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI</title>
<link rel="stylesheet" href="/static/css/main.css">
<style>
.hero{text-align:center;padding:80px 20px 30px}
.hero h1{font-size:clamp(42px,9vw,96px);font-weight:900;letter-spacing:8px;
  background:linear-gradient(135deg,
    #a855f7 0%,#22d3ee 25%,#fbbf24 50%,#f472b6 75%,#a855f7 100%);
  background-size:400% 400%;
  -webkit-background-clip:text;background-clip:text;color:transparent;
  animation:shine 8s ease infinite;
  filter:drop-shadow(0 0 40px rgba(168,85,247,0.7))
         drop-shadow(0 0 20px rgba(34,211,238,0.5))}
.hero .sub{margin-top:20px;color:var(--muted);font-size:18px;
  letter-spacing:2px;font-weight:500}
.hero .line{width:120px;height:2px;margin:28px auto;
  background:linear-gradient(90deg,transparent,var(--c2),
    var(--c1),var(--c3),transparent);
  box-shadow:0 0 20px var(--c2);animation:linepulse 3s infinite}
@keyframes linepulse{0%,100%{opacity:.6;width:120px}50%{opacity:1;width:180px}}
.cards{max-width:1100px;margin:40px auto;padding:0 20px;
  display:grid;gap:20px;
  grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.card{padding:28px 24px;border-radius:22px;text-decoration:none;
  color:var(--text);
  background:linear-gradient(135deg,
    rgba(30,27,75,0.65),rgba(49,46,129,0.5));
  backdrop-filter:blur(24px);border:1px solid var(--border);
  position:relative;overflow:hidden;
  transition:transform .35s cubic-bezier(.2,.8,.2,1),
             box-shadow .35s,border-color .35s}
.card:hover{transform:translateY(-8px) scale(1.02);
  border-color:var(--c2);
  box-shadow:0 20px 60px rgba(168,85,247,0.5),
             0 0 40px rgba(34,211,238,0.3)}
.card .icon{font-size:32px;color:var(--c2);margin-bottom:16px;
  display:flex;align-items:center;gap:10px;
  filter:drop-shadow(0 0 12px var(--c2))}
.card .num{color:var(--muted);font-size:12px;letter-spacing:2px}
.card h3{font-size:20px;margin-bottom:10px;font-weight:700;
  background:linear-gradient(90deg,var(--c1),var(--c2));
  -webkit-background-clip:text;background-clip:text;color:transparent}
.card p{color:var(--muted);font-size:14px;line-height:1.8}
.foot{text-align:center;padding:60px 20px;color:var(--muted);
  font-size:13px;letter-spacing:1px}
.foot .sym{color:var(--c2);margin:0 8px}
</style>
</head>
<body>
<div class="topbar">
  <span class="brand">AL-KHALLAQI</span>
  <span class="chip">الإبداع بلا حدود</span>
</div>
<div class="hero">
  <h1>AL-KHALLAQI</h1>
  <div class="line"></div>
  <div class="sub">وكيل الذكاء الاصطناعي الإبداعي</div>
</div>
<div class="cards">
  <a class="card" href="/creative">
    <div class="icon">&#x2B22; <span class="num">01</span></div>
    <h3>الواجهة الإبداعية</h3>
    <p>تحدّث بالصوت أو الكتابة. الوكيل يفهمك ويجيبك.</p>
  </a>
  <a class="card" href="/studio">
    <div class="icon">&#x27C1; <span class="num">02</span></div>
    <h3>الاستوديو</h3>
    <p>صور، فيديو، نصوص، شعارات، وهويات بصرية.</p>
  </a>
  <a class="card" href="/gallery">
    <div class="icon">&#x25C8; <span class="num">03</span></div>
    <h3>المعرض</h3>
    <p>كل ما أنشأته محفوظ هنا.</p>
  </a>
  <a class="card" href="/apk">
    <div class="icon">&#x27D0; <span class="num">04</span></div>
    <h3>بناء APK</h3>
    <p>حوّل المشروع إلى تطبيق أندرويد جاهز.</p>
  </a>
  <a class="card" href="/vault/hg2026">
    <div class="icon">&#x232C; <span class="num">05</span></div>
    <h3>لوحة التحكم</h3>
    <p>إدارة مفاتيح API والإحصائيات.</p>
  </a>
  <a class="card" href="/docs">
    <div class="icon">&#x27E1; <span class="num">06</span></div>
    <h3>توثيق API</h3>
    <p>المسارات التفاعلية الكاملة.</p>
  </a>
</div>
<div class="foot">
  Hussein Ghallab <span class="sym">&#x2B22;</span> AL-KHALLAQI v1.0
</div>
</body>
</html>
'''
w("templates/choice.html", CHOICE)

# ═══════════════════════════════════════════════════════════
# inline_templates.py — كل الصفحات
# ═══════════════════════════════════════════════════════════
CSS = (BASE / "static" / "css" / "main.css").read_text(encoding="utf-8")

lines = ['# Auto-generated by fix_all_pages.py', '']
lines.append('CSS = ' + repr(CSS))
lines.append('')
lines.append('TEMPLATES = {')
for name, html in [('choice.html', CHOICE), ('studio.html', STUDIO),
                    ('gallery.html', GALLERY), ('work_view.html', WORK_VIEW),
                    ('apk.html', APK)]:
    lines.append(f'    {name!r}: {html!r},')
# احتفظ بالقديم من creative.html و admin.html إذا موجودين
for fname in ['creative.html', 'admin.html']:
    fp = BASE / "templates" / fname
    if fp.exists():
        content = fp.read_text(encoding="utf-8")
        lines.append(f'    {fname!r}: {content!r},')
lines.append('}')
w("app/inline_templates.py", "\n".join(lines))

# ═══════════════════════════════════════════════════════════
# تأكد من main.py
# ═══════════════════════════════════════════════════════════
main_path = BASE / "app" / "main.py"
src = main_path.read_text(encoding="utf-8")

# تأكد أن /studio و /gallery و /work موجودة
for route, name in [("/studio", "studio_ui"), ("/gallery", "gallery_ui"),
                     ("/apk", "apk_page")]:
    if f'@app.get("{route}"' not in src:
        src = src.rstrip() + f'''

@app.get("{route}", response_class=HTMLResponse)
async def {name}(request: Request):
    return _render("{route.strip('/')}.html", request)
'''
        print(f"[+] main.py ({route})")

if "/work/{wid}" not in src:
    src = src.rstrip() + '''

@app.get("/work/{wid}", response_class=HTMLResponse)
async def work_view_page(wid: int, request: Request):
    return _render("work_view.html", request, work_id=wid)
'''
    print("[+] main.py (/work/{wid})")

main_path.write_text(src, encoding="utf-8")

print()
print("=" * 60)
print("  اكتمل الإصلاح")
print("=" * 60)
print()
print("  ✓ studio.html ✓ gallery.html")
print("  ✓ work_view.html ✓ apk.html")
print("  ✓ choice.html (رموز مستقبلية)")
print("  ✓ inline_templates: كل الصفحات")
print("  ✓ main.py: كل المسارات")
print()
print("  الرموز الجديدة:")
print("    ⬢ صور    ⟁ فيديو    ◈ نصوص")
print("    ⧊ هوية   ⍟ وكيل    ⎔ محادثة")
print("    ⌬ إدارة   ⟐ APK     ⟡ توثيق")
print()
print("ارفع:")
print("   git add -A")
print('   git commit -m "Fix all pages + futuristic symbols"')
print("   git push origin main")
print("=" * 60)
