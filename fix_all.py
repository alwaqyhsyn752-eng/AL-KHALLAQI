#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AL-KHALLAQI — Full fix: inline templates + new relaxing theme + no emojis."""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

# ═════════════════════════════════════════════════════════════
# 1) SHARED CSS — relaxing palette
# ═════════════════════════════════════════════════════════════
CSS = r'''*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0a0e1a;--bg2:#131a2c;
  --card:rgba(20,30,50,0.65);
  --border:rgba(125,211,252,0.22);
  --primary:#7dd3fc;--primary2:#38bdf8;
  --teal:#5eead4;--gold:#fcd34d;
  --rose:#fda4af;--lavender:#a5b4fc;
  --text:#e2e8f0;--muted:#94a3b8;
}
html,body{height:100%}
body{
  font-family:'Poppins','Segoe UI',system-ui,sans-serif;
  background:var(--bg);color:var(--text);overflow-x:hidden;
  min-height:100vh;position:relative;line-height:1.6;
}
body::before{
  content:"";position:fixed;inset:-20%;z-index:-2;
  background:
    radial-gradient(circle at 15% 20%,rgba(125,211,252,0.18),transparent 45%),
    radial-gradient(circle at 85% 30%,rgba(94,234,212,0.14),transparent 45%),
    radial-gradient(circle at 50% 85%,rgba(165,180,252,0.15),transparent 50%);
  filter:blur(70px);animation:aurora 22s ease-in-out infinite alternate;
}
body::after{
  content:"";position:fixed;inset:0;z-index:-1;
  background-image:
    linear-gradient(rgba(125,211,252,0.04) 1px,transparent 1px),
    linear-gradient(90deg,rgba(125,211,252,0.04) 1px,transparent 1px);
  background-size:48px 48px;
  mask-image:radial-gradient(circle at center,black,transparent 85%);
}
@keyframes aurora{
  0%{transform:translate(0,0) scale(1)}
  50%{transform:translate(2%,-1.5%) scale(1.06)}
  100%{transform:translate(-1.5%,1.5%) scale(1.02)}
}
.glass{
  background:var(--card);
  backdrop-filter:blur(20px) saturate(150%);
  -webkit-backdrop-filter:blur(20px) saturate(150%);
  border:1px solid var(--border);border-radius:20px;
  box-shadow:0 8px 40px rgba(10,14,26,0.5),inset 0 1px 0 rgba(255,255,255,0.04);
}
.btn{
  display:inline-flex;align-items:center;justify-content:center;gap:8px;
  padding:12px 22px;border-radius:14px;border:1px solid var(--border);
  background:linear-gradient(135deg,var(--primary2),var(--teal));
  color:#0a0e1a;font-weight:700;cursor:pointer;font-family:inherit;font-size:15px;
  transition:transform .25s cubic-bezier(.2,.8,.2,1),box-shadow .25s;
  box-shadow:0 4px 22px rgba(56,189,248,0.3);
}
.btn:hover{transform:translateY(-2px);box-shadow:0 8px 32px rgba(56,189,248,0.5)}
.input,textarea,select{
  width:100%;padding:12px 14px;border-radius:12px;
  background:rgba(10,14,26,0.7);border:1px solid var(--border);
  color:var(--text);font-family:inherit;font-size:15px;outline:none;
  transition:border-color .2s,box-shadow .2s;
}
.input:focus,textarea:focus,select:focus{
  border-color:var(--primary);box-shadow:0 0 0 3px rgba(125,211,252,0.15);
}
.topbar{
  position:sticky;top:0;z-index:20;padding:14px 20px;
  display:flex;align-items:center;justify-content:space-between;
  background:rgba(10,14,26,0.75);backdrop-filter:blur(18px);
  border-bottom:1px solid var(--border);
}
.brand{
  font-weight:800;font-size:20px;letter-spacing:2px;
  color:var(--primary);
}
.brand .sym{color:var(--teal);margin:0 6px}
.muted{color:var(--muted)}
.chip{
  display:inline-block;padding:5px 12px;border-radius:999px;
  background:rgba(125,211,252,0.1);border:1px solid var(--border);
  color:var(--muted);font-size:12px;letter-spacing:.5px;
}
.grid{display:grid;gap:18px}
.g2{grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}
.pulse{animation:pulse 2.4s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.7}}
.sym{color:var(--teal)}
'''

# ═════════════════════════════════════════════════════════════
# 2) PAGE TEMPLATES
# ═════════════════════════════════════════════════════════════
CHOICE = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI</title>
<style>__CSS__
.hero{text-align:center;padding:90px 20px 40px;position:relative}
.hero h1{
  font-size:clamp(38px,8vw,84px);font-weight:800;letter-spacing:8px;
  color:var(--primary);
}
.hero h1 .dot{color:var(--teal);font-size:.5em;vertical-align:middle;margin:0 8px}
.hero .sub{margin-top:16px;color:var(--muted);font-size:17px;letter-spacing:1px}
.hero .line{
  width:80px;height:2px;margin:24px auto;
  background:linear-gradient(90deg,transparent,var(--teal),transparent);
}
.cards{max-width:1100px;margin:30px auto;padding:0 20px;
  display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(250px,1fr))}
.card{
  padding:28px 24px;border-radius:20px;text-decoration:none;color:var(--text);
  background:var(--card);backdrop-filter:blur(20px);
  border:1px solid var(--border);position:relative;
  transition:transform .3s cubic-bezier(.2,.8,.2,1),box-shadow .3s,border-color .3s;
}
.card:hover{transform:translateY(-5px);border-color:var(--primary);
  box-shadow:0 18px 48px rgba(56,189,248,0.18)}
.card .icon{
  font-size:26px;color:var(--teal);margin-bottom:14px;letter-spacing:2px;
  display:flex;align-items:center;gap:8px;
}
.card .icon .num{color:var(--muted);font-size:12px;letter-spacing:1px}
.card h3{font-size:19px;margin-bottom:8px;color:var(--primary);font-weight:700}
.card p{color:var(--muted);font-size:14px;line-height:1.7}
.foot{text-align:center;padding:50px 20px;color:var(--muted);font-size:13px;letter-spacing:.5px}
.foot .sym{color:var(--teal);margin:0 6px}
</style>
</head>
<body>
<div class="topbar">
  <span class="brand">AL-KHALLAQI</span>
  <span class="chip">الإبداع بلا حدود</span>
</div>
<div class="hero">
  <h1>AL<span class="dot">✦</span>KHALLAQI</h1>
  <div class="line"></div>
  <div class="sub">وكيل الذكاء الاصطناعي الإبداعي — Hussein Ghallab</div>
</div>
<div class="cards">
  <a class="card" href="/creative">
    <div class="icon">✦ <span class="num">01</span></div>
    <h3>الواجهة الإبداعية</h3>
    <p>تحدّث مع الوكيل الذكي واطلب أفكاراً ومشاريع.</p>
  </a>
  <a class="card" href="/studio">
    <div class="icon">◆ <span class="num">02</span></div>
    <h3>استوديو الإبداع</h3>
    <p>صور، فيديو، نصوص، شعارات، وهويات بصرية.</p>
  </a>
  <a class="card" href="/gallery">
    <div class="icon">❖ <span class="num">03</span></div>
    <h3>معرض الأعمال</h3>
    <p>تصفّح كل ما أنشأته، احفظه وشاركه.</p>
  </a>
  <a class="card" href="/admin">
    <div class="icon">⬢ <span class="num">04</span></div>
    <h3>لوحة الإدارة</h3>
    <p>إحصائيات النظام ومزودو الذكاء الاصطناعي.</p>
  </a>
  <a class="card" href="/docs">
    <div class="icon">▸ <span class="num">05</span></div>
    <h3>توثيق API</h3>
    <p>كل المسارات المتاحة مع أمثلة تفاعلية.</p>
  </a>
  <a class="card" href="/api/v1/health">
    <div class="icon">● <span class="num">06</span></div>
    <h3>حالة النظام</h3>
    <p>تحقق من صحة النظام والمزودين.</p>
  </a>
</div>
<div class="foot">
  <span class="sym">✦</span> Hussein Ghallab <span class="sym">✦</span> AL-KHALLAQI v1.0
</div>
</body>
</html>'''

CREATIVE = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — الواجهة الإبداعية</title>
<style>__CSS__
.wrap{max-width:900px;margin:0 auto;padding:20px}
.toolbar{display:flex;gap:8px;overflow-x:auto;padding:14px 0;scrollbar-width:none}
.toolbar::-webkit-scrollbar{display:none}
.tool{padding:10px 18px;border-radius:12px;border:1px solid var(--border);
  background:rgba(10,14,26,0.5);color:var(--muted);cursor:pointer;
  white-space:nowrap;font-weight:600;font-size:14px;transition:.25s;
  font-family:inherit}
.tool:hover,.tool.active{background:linear-gradient(135deg,var(--primary2),var(--teal));
  color:#0a0e1a;border-color:transparent}
.chat{display:flex;flex-direction:column;gap:16px;margin:20px 0;min-height:50vh}
.msg{padding:16px 20px;border-radius:18px;max-width:85%;line-height:1.7;
  animation:rise .35s cubic-bezier(.2,.8,.2,1);word-wrap:break-word}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.msg.user{align-self:flex-start;
  background:linear-gradient(135deg,var(--primary2),var(--teal));
  color:#0a0e1a;font-weight:600}
.msg.bot{align-self:flex-end;background:var(--card);border:1px solid var(--border);
  backdrop-filter:blur(14px)}
.msg img,.msg svg{max-width:100%;border-radius:14px;margin-top:10px;display:block}
.composer{position:sticky;bottom:0;padding:16px 0;
  background:linear-gradient(to top,rgba(10,14,26,0.98),transparent)}
.composer-inner{display:flex;gap:10px;align-items:flex-end}
textarea#inp{resize:none;min-height:52px;max-height:200px}
.send{width:52px;height:52px;border-radius:50%;padding:0;font-size:20px}
</style>
</head>
<body>
<div class="topbar">
  <span class="brand">AL<span class="sym">✦</span>KHALLAQI</span>
  <span class="chip">وضع إبداعي</span>
</div>
<div class="wrap">
  <div class="toolbar" id="tools">
    <button class="tool active" data-t="image">✦ صور</button>
    <button class="tool" data-t="video">◆ فيديو</button>
    <button class="tool" data-t="text">❖ نصوص</button>
    <button class="tool" data-t="logo">⬢ شعار</button>
    <button class="tool" data-t="identity">◈ هوية</button>
    <button class="tool" data-t="agent">✧ وكيل</button>
  </div>
  <div class="chat" id="chat">
    <div class="msg bot">أهلاً بك في <b style="color:var(--primary)">AL-KHALLAQI</b>
    <br>اختر أداة وابدأ الإبداع. اكتب فكرتك وسأحوّلها إلى واقع.</div>
  </div>
  <div class="composer">
    <div class="composer-inner">
      <textarea id="inp" placeholder="اكتب فكرتك..."></textarea>
      <button class="btn send" id="send">▸</button>
    </div>
  </div>
</div>
<script>
const chat=document.getElementById('chat');
const inp=document.getElementById('inp');
const send=document.getElementById('send');
let currentTool='image';
document.querySelectorAll('.tool').forEach(t=>{
  t.addEventListener('click',()=>{
    document.querySelectorAll('.tool').forEach(x=>x.classList.remove('active'));
    t.classList.add('active');currentTool=t.dataset.t;
    inp.placeholder={image:'صف الصورة...',video:'صف الفيديو...',
      text:'موضوع المقال أو القصة...',logo:'اسم العلامة...',
      identity:'اسم المشروع والمجال...',agent:'اكتب هدفاً كاملاً...'}[currentTool]||'اكتب...';
  });
});
function addMsg(cls,html){
  const d=document.createElement('div');
  d.className='msg '+cls;d.innerHTML=html;
  chat.appendChild(d);chat.scrollTop=chat.scrollHeight;return d;
}
inp.addEventListener('input',()=>{inp.style.height='auto';
  inp.style.height=Math.min(inp.scrollHeight,200)+'px';});
inp.addEventListener('keydown',e=>{
  if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();doSend();}
});
async function api(path,body){
  const r=await fetch('/api/v1'+path,{method:'POST',
    headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  if(!r.ok) throw new Error(await r.text());
  return r.json();
}
async function doSend(){
  const v=inp.value.trim();if(!v) return;
  inp.value='';inp.style.height='52px';
  addMsg('user',v);
  const bot=addMsg('bot','<span class="pulse">جارٍ المعالجة...</span>');
  try{
    if(currentTool==='image'){
      const d=await api('/creative/image',{prompt:v});
      bot.innerHTML='<b style="color:var(--primary)">✦ صورة مولّدة</b><br>'
        +'<span class="muted">'+d.prompt+'</span><img src="'+d.url+'"/>';
    } else if(currentTool==='video'){
      const d=await api('/creative/video',{prompt:v});
      bot.innerHTML='<b style="color:var(--primary)">◆ فيديو قصير</b>';
      if(d.gif){const img=document.createElement('img');img.src=d.gif;bot.appendChild(img);}
      else bot.innerHTML+='<br>'+d.frames.map(u=>'<img src="'+u+'"/>').join('');
    } else if(currentTool==='text'){
      const d=await api('/creative/text',{prompt:v,kind:'article'});
      bot.innerHTML='<b style="color:var(--primary)">❖ نص مولّد</b><br>'
        +d.text.replace(/\n/g,'<br>');
    } else if(currentTool==='logo'){
      const d=await api('/studio/logo',{brand:v});
      bot.innerHTML='<b style="color:var(--primary)">⬢ شعار</b><br>'+d.svg;
    } else if(currentTool==='identity'){
      const d=await api('/studio/identity',{brand:v});
      const pal=(d.palette||[]).map(c=>'<span style="display:inline-block;width:26px;height:26px;border-radius:6px;background:'+c+';margin:2px"></span>').join('');
      bot.innerHTML='<b style="color:var(--primary)">◈ هوية بصرية</b><br>'
        +'<b>'+d.brand+'</b><br><i>'+(d.tagline||'')+'</i><br>'+pal
        +'<br>'+(d.logo_svg||'');
    } else if(currentTool==='agent'){
      const d=await api('/agent/run',{goal:v,max_steps:6});
      let html='<b style="color:var(--primary)">✧ نتيجة الوكيل</b><br>';
      (d.steps||[]).forEach(s=>{
        html+='<div style="margin:8px 0;padding:10px;border-right:3px solid var(--teal);'
          +'background:rgba(94,234,212,0.06);border-radius:8px">'
          +'<b>خطوة '+s.step+'</b> <span class="muted">'+s.action+'</span><br>'
          +'<span>'+s.thought+'</span></div>';
      });
      html+='<hr style="border-color:var(--border);margin:12px 0"><b>الإجابة:</b><br>'
        +d.final_answer;
      bot.innerHTML=html;
    }
  }catch(e){bot.innerHTML='<b style="color:#f87171">خطأ</b><br>'+e.message;}
  chat.scrollTop=chat.scrollHeight;
}
send.addEventListener('click',doSend);
</script>
</body>
</html>'''

STUDIO = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — الاستوديو</title>
<style>__CSS__
.wrap{max-width:1100px;margin:0 auto;padding:22px}
.tabs{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:22px}
.tab{padding:11px 20px;border-radius:12px;border:1px solid var(--border);
  background:rgba(10,14,26,0.5);color:var(--muted);cursor:pointer;font-weight:600;
  font-family:inherit;font-size:14px;transition:.25s}
.tab.active{background:linear-gradient(135deg,var(--primary2),var(--teal));
  color:#0a0e1a;border-color:transparent}
.panel{display:none;padding:26px}
.panel.active{display:block}
.row{display:grid;gap:12px;grid-template-columns:1fr 1fr;margin-bottom:14px}
.row.full{grid-template-columns:1fr}
.preview{margin-top:22px;min-height:200px;padding:18px;border-radius:16px;
  background:rgba(10,14,26,0.55);border:1px dashed var(--border)}
.preview img,.preview svg{max-width:100%;border-radius:12px}
h3{color:var(--primary);font-weight:700;letter-spacing:.5px}
h3 .sym{color:var(--teal);margin-left:8px}
</style>
</head>
<body>
<div class="topbar"><span class="brand">AL<span class="sym">✦</span>KHALLAQI</span>
<span class="chip">الاستوديو</span></div>
<div class="wrap">
  <div class="tabs">
    <button class="tab active" data-p="images">✦ صور</button>
    <button class="tab" data-p="video">◆ فيديو</button>
    <button class="tab" data-p="text">❖ نصوص</button>
    <button class="tab" data-p="identity">◈ هويات</button>
  </div>

  <div class="glass panel active" id="images">
    <h3>توليد صورة <span class="sym">✦</span></h3><br>
    <div class="row full"><textarea class="input" id="imgPrompt" rows="3" placeholder="صف الصورة..."></textarea></div>
    <div class="row">
      <select class="input" id="imgStyle">
        <option value="realistic">واقعي</option><option value="artistic">فني</option>
        <option value="cyberpunk">سايبربانك</option><option value="anime">أنمي</option>
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
    <h3>توليد فيديو <span class="sym">◆</span></h3><br>
    <div class="row full"><textarea class="input" id="vidPrompt" rows="3" placeholder="صف الفيديو..."></textarea></div>
    <div class="row">
      <select class="input" id="vidAspect">
        <option value="16:9">16:9</option><option value="9:16">9:16</option><option value="1:1">1:1</option>
      </select>
      <input class="input" id="vidDur" type="number" value="4" min="2" max="10">
    </div>
    <button class="btn" onclick="genVideo()">توليد</button>
    <div class="preview" id="vidPrev">النتيجة ستظهر هنا</div>
  </div>

  <div class="glass panel" id="text">
    <h3>توليد نص <span class="sym">❖</span></h3><br>
    <div class="row full"><textarea class="input" id="txtPrompt" rows="3" placeholder="الموضوع..."></textarea></div>
    <div class="row">
      <select class="input" id="txtKind">
        <option value="article">مقال</option><option value="story">قصة</option>
        <option value="script">سيناريو</option>
      </select>
      <select class="input" id="txtTone">
        <option value="creative">إبداعي</option><option value="formal">رسمي</option>
        <option value="fun">مرح</option>
      </select>
    </div>
    <button class="btn" onclick="genText()">توليد</button>
    <div class="preview" id="txtPrev">النتيجة ستظهر هنا</div>
  </div>

  <div class="glass panel" id="identity">
    <h3>بناء هوية بصرية <span class="sym">◈</span></h3><br>
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
    headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  if(!r.ok) throw new Error(await r.text());
  return r.json();
}
async function genImage(){
  const p=document.getElementById('imgPrompt').value.trim();if(!p)return;
  const s=document.getElementById('imgStyle').value;
  const [w,h]=document.getElementById('imgSize').value.split('x').map(Number);
  const prev=document.getElementById('imgPrev');prev.textContent='جارٍ التوليد...';
  try{const d=await post('/creative/image',{prompt:p,style:s,width:w,height:h});
    prev.innerHTML='<img src="'+d.url+'"/>';}
  catch(e){prev.textContent='خطأ: '+e.message;}
}
async function genVideo(){
  const p=document.getElementById('vidPrompt').value.trim();if(!p)return;
  const prev=document.getElementById('vidPrev');prev.textContent='جارٍ التوليد... (قد يستغرق دقيقة)';
  try{const d=await post('/creative/video',{prompt:p,
    aspect:document.getElementById('vidAspect').value,
    duration:Number(document.getElementById('vidDur').value)||4});
    if(d.gif){prev.innerHTML='<img src="'+d.gif+'"/>';}
    else{prev.innerHTML=d.frames.map(u=>'<img style="max-width:180px;margin:4px" src="'+u+'"/>').join('');}}
  catch(e){prev.textContent='خطأ: '+e.message;}
}
async function genText(){
  const p=document.getElementById('txtPrompt').value.trim();if(!p)return;
  const prev=document.getElementById('txtPrev');prev.textContent='جارٍ الكتابة...';
  try{const d=await post('/creative/text',{prompt:p,
    kind:document.getElementById('txtKind').value,
    tone:document.getElementById('txtTone').value});
    prev.innerHTML=d.text.replace(/\n/g,'<br>');}
  catch(e){prev.textContent='خطأ: '+e.message;}
}
async function genIdentity(){
  const b=document.getElementById('idBrand').value.trim();if(!b)return;
  const prev=document.getElementById('idPrev');prev.textContent='جارٍ البناء...';
  try{const d=await post('/studio/identity',{brand:b,
    industry:document.getElementById('idIndustry').value});
    const pal=(d.palette||[]).map(c=>'<span style="display:inline-block;width:32px;height:32px;border-radius:8px;background:'+c+';margin:3px"></span>').join('');
    prev.innerHTML='<b>'+d.brand+'</b><br><i>'+(d.tagline||'')+'</i><br>'
      +'<div style="margin:10px 0">'+pal+'</div>'+(d.logo_svg||'');}
  catch(e){prev.textContent='خطأ: '+e.message;}
}
</script>
</body></html>'''

GALLERY = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — المعرض</title>
<style>__CSS__
.wrap{max-width:1100px;margin:0 auto;padding:22px}
.cardwork{padding:16px;border-radius:18px;background:var(--card);
  border:1px solid var(--border);transition:.3s;cursor:pointer;text-decoration:none;color:inherit;display:block}
.cardwork:hover{transform:translateY(-4px);border-color:var(--primary);
  box-shadow:0 14px 40px rgba(56,189,248,0.18)}
.cardwork .kind{font-size:11px;color:var(--teal);letter-spacing:2px;text-transform:uppercase}
.cardwork h4{margin:10px 0 6px;color:var(--primary);font-weight:700}
.empty{padding:80px 20px;text-align:center;color:var(--muted)}
.empty .sym{color:var(--teal);font-size:32px;display:block;margin-bottom:14px}
</style></head>
<body>
<div class="topbar"><span class="brand">AL<span class="sym">✦</span>KHALLAQI</span>
<span class="chip">المعرض</span></div>
<div class="wrap">
  <h2 style="color:var(--primary);margin-bottom:20px;letter-spacing:1px">❖ معرض الأعمال</h2>
  <div class="grid g2" id="grid"></div>
  <div class="empty" id="empty" style="display:none">
    <span class="sym">✦</span>
    لا توجد أعمال بعد. ابدأ من <a href="/studio" style="color:var(--teal)">الاستوديو</a>.
  </div>
</div>
<script>
(async()=>{
  const r=await fetch('/api/v1/gallery/works?limit=100');
  const d=await r.json();
  const grid=document.getElementById('grid');
  if(!d.works||!d.works.length){document.getElementById('empty').style.display='block';return;}
  d.works.forEach(w=>{
    const a=document.createElement('a');
    a.href='/work/'+w.id;a.className='cardwork';
    a.innerHTML='<div class="kind">'+w.kind+'</div>'
      +'<h4>'+w.title+'</h4>'
      +'<div class="muted" style="font-size:12px">'+(w.created_at||'').split('T')[0]+'</div>';
    grid.appendChild(a);
  });
})();
</script>
</body></html>'''

WORK_VIEW = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — عرض العمل</title>
<style>__CSS__
.wrap{max-width:900px;margin:0 auto;padding:26px}
.body{padding:26px;border-radius:20px;background:var(--card);border:1px solid var(--border)}
.body img,.body svg{max-width:100%;border-radius:14px;display:block;margin:14px 0}
.actions{display:flex;gap:10px;margin-top:22px}
h2{color:var(--primary);letter-spacing:1px}
</style></head>
<body>
<div class="topbar"><span class="brand">AL<span class="sym">✦</span>KHALLAQI</span>
<span class="chip">عرض عمل</span></div>
<div class="wrap">
  <div class="body" id="body">جارٍ التحميل...</div>
  <div class="actions" id="actions"></div>
</div>
<script>
const wid=location.pathname.split('/').pop();
(async()=>{
  const r=await fetch('/api/v1/gallery/works/'+wid);
  if(!r.ok){document.getElementById('body').textContent='غير موجود';return;}
  const w=await r.json();
  const b=document.getElementById('body');
  let html='<h2>'+w.title+'</h2><div class="chip" style="margin:10px 0">'+w.kind+'</div>';
  if(w.prompt) html+='<p class="muted">'+w.prompt+'</p>';
  if(w.content) html+='<div>'+w.content+'</div>';
  const ex=w.extra||{};
  if(ex.url) html+='<img src="'+ex.url+'"/>';
  if(ex.svg) html+=ex.svg;
  if(ex.text) html+='<div>'+ex.text.replace(/\n/g,'<br>')+'</div>';
  b.innerHTML=html;
  document.getElementById('actions').innerHTML=
    '<button class="btn" onclick="history.back()">رجوع ▸</button>';
})();
</script>
</body></html>'''

ADMIN = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — الإدارة</title>
<style>__CSS__
.wrap{max-width:900px;margin:0 auto;padding:26px}
.stat{padding:22px;border-radius:16px;background:var(--card);border:1px solid var(--border)}
.stat b{font-size:34px;display:block;color:var(--teal);font-weight:800;letter-spacing:1px}
.stat .lbl{color:var(--muted);font-size:13px;letter-spacing:1px;margin-top:6px}
h2{color:var(--primary);letter-spacing:1px}
</style></head>
<body>
<div class="topbar"><span class="brand">AL<span class="sym">✦</span>KHALLAQI</span>
<span class="chip">الإدارة</span></div>
<div class="wrap">
  <h2 style="margin-bottom:20px">⬢ لوحة الإدارة</h2>
  <div style="display:flex;gap:12px;margin-bottom:22px">
    <input class="input" id="pwd" type="password" placeholder="كلمة المرور">
    <button class="btn" onclick="load()">دخول</button>
  </div>
  <div class="grid g2" id="stats"></div>
</div>
<script>
async function load(){
  const p=document.getElementById('pwd').value;
  const r=await fetch('/api/v1/admin/stats',{headers:{'X-Admin-Password':p}});
  const out=document.getElementById('stats');
  if(!r.ok){out.innerHTML='<div class="stat"><b>!</b><span class="lbl">كلمة مرور خاطئة</span></div>';return;}
  const d=await r.json();
  out.innerHTML=
    '<div class="stat"><b>'+d.total_works+'</b><span class="lbl">إجمالي الأعمال</span></div>'
    +'<div class="stat"><b>'+Object.keys(d.providers||{}).length+'</b><span class="lbl">مزودو الذكاء</span></div>'
    +Object.entries(d.providers||{}).map(([k,v])=>
      '<div class="stat"><b>'+(v?'●':'○')+'</b><span class="lbl">'+k+'</span></div>').join('')
    +Object.entries(d.by_kind||{}).map(([k,v])=>
      '<div class="stat"><b>'+v+'</b><span class="lbl">'+k+'</span></div>').join('');
}
</script>
</body></html>'''

PAGES = {
    "choice.html": CHOICE,
    "creative.html": CREATIVE,
    "studio.html": STUDIO,
    "gallery.html": GALLERY,
    "work_view.html": WORK_VIEW,
    "admin.html": ADMIN,
}

# ═════════════════════════════════════════════════════════════
# 3) WRITE FILES
# ═════════════════════════════════════════════════════════════
def step(n, t):
    print("\n" + "=" * 60)
    print(f"  الخطوة {n}: {t}")
    print("=" * 60)

step(1, "إنشاء قوالب HTML جديدة")
tpl_dir = BASE / "templates"
tpl_dir.mkdir(exist_ok=True)
for name, html in PAGES.items():
    content = html.replace("__CSS__", CSS)
    (tpl_dir / name).write_text(content, encoding="utf-8")
    print(f"  [+] templates/{name}")

step(2, "إنشاء static/css/main.css")
css_dir = BASE / "static" / "css"
css_dir.mkdir(parents=True, exist_ok=True)
(css_dir / "main.css").write_text(CSS, encoding="utf-8")
print("  [+] static/css/main.css")

step(3, "إنشاء قوالب مدمجة في بايثون")
inline = ["# Auto-generated by fix_all.py — inline HTML templates", ""]
inline.append("TEMPLATES = {")
for name, html in PAGES.items():
    content = html.replace("__CSS__", CSS)
    inline.append(f"    {name!r}: {content!r},")
inline.append("}")
inline.append("")
inline.append("CSS = " + repr(CSS))
(BASE / "app" / "inline_templates.py").write_text("\n".join(inline), encoding="utf-8")
print("  [+] app/inline_templates.py")

step(4, "تحديث app/main.py لدعم القوالب المدمجة")

main_path = BASE / "app" / "main.py"
src = main_path.read_text(encoding="utf-8")

# أضف import
if "inline_templates" not in src:
    src = src.replace(
        "from app.db.redis import close_cache",
        "from app.db.redis import close_cache\nfrom app import inline_templates"
    )

# استبدل دالة _render
import re
pattern = re.compile(
    r"def _render\(name: str, request: Request, \*\*kw\):.*?(?=\n@app\.get|\Z)",
    re.DOTALL
)

NEW_RENDER = '''def _render(name: str, request: Request, **kw):
    """Render with filesystem first, inline fallback second."""
    # 1) filesystem
    try:
        if TEMPLATES_DIR.exists() and (TEMPLATES_DIR / name).exists():
            return templates.TemplateResponse(
                name, {"request": request, "settings": settings, **kw})
    except Exception as e:
        log.warning("fs render failed for %s: %s", name, e)

    # 2) inline fallback
    if name in inline_templates.TEMPLATES:
        log.info("using inline template: %s", name)
        return HTMLResponse(inline_templates.TEMPLATES[name])

    # 3) last resort
    return HTMLResponse(
        f"<html><body style='background:#0a0e1a;color:#e2e8f0;"
        f"font-family:sans-serif;padding:40px;text-align:center'>"
        f"<h1 style='color:#7dd3fc'>{settings.APP_NAME}</h1>"
        f"<p>الصفحة ({name}) غير متوفرة. "
        f"<a style='color:#5eead4' href='/'>العودة</a></p></body></html>")


'''

if pattern.search(src):
    src = pattern.sub(NEW_RENDER, src)
    print("  [+] تم استبدال _render")
else:
    print("  [!] لم أجد _render — سأتخطى")

main_path.write_text(src, encoding="utf-8")

step(5, "رفع على GitHub")
cmds = [
    'git add -A',
    'git commit -m "New theme: relaxing colors + decorative symbols + inline templates fallback"',
    'git push origin main',
]
for c in cmds:
    print(f"\n$ {c}")
    r = subprocess.run(c, shell=True, cwd=BASE, text=True)
    if c.startswith('git push') and r.returncode != 0:
        print("\n❌ فشل الرفع — تحقق من التوكن")
        break

print("\n" + "=" * 60)
print("  ✦ اكتمل")
print("=" * 60)
print("\nالخطوة التالية:")
print("  1. افتح Render → al-khallaqi")
print("  2. Manual Deploy → Clear build cache & deploy")
print("  3. افتح https://al-khallaqi.onrender.com")
