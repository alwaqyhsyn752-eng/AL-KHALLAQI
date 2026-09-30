#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""إجبار Render على استخدام الواجهات الجديدة."""
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent

def w(rel, content):
    p = BASE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"[+] {rel}")

# ═══════════════════════════════════════════════════════════
# 1) احذف inline_templates القديم (نعيد إنشاءه)
# ═══════════════════════════════════════════════════════════
old_inline = BASE / "app" / "inline_templates.py"
if old_inline.exists():
    old_inline.unlink()
    print("[x] حذفت inline_templates.py القديم")

# ═══════════════════════════════════════════════════════════
# 2) CSS — بلورات كريستالية متحركة
# ═══════════════════════════════════════════════════════════
CSS = r'''/* AL-KHALLAQI — Crystal Prism 2026 */
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --c1:#a855f7;--c2:#22d3ee;--c3:#fbbf24;--c4:#f472b6;
  --c5:#06b6d4;--c6:#8b5cf6;--c7:#fde68a;
  --bg:#05030f;--card:rgba(30,27,75,0.55);
  --border:rgba(168,85,247,0.4);
  --text:#f5f3ff;--muted:#c4b5fd;
}
html,body{height:100%}
body{font-family:'Poppins','Segoe UI',system-ui,sans-serif;
  background:var(--bg);color:var(--text);overflow-x:hidden;
  min-height:100vh;position:relative;line-height:1.6}

/* طبقة الألوان المتبلورة المتحركة */
body::before{content:"";position:fixed;inset:-30%;z-index:-2;
  background:
    conic-gradient(from 0deg at 30% 30%,
      rgba(168,85,247,0.4),rgba(34,211,238,0.35),
      rgba(251,191,36,0.3),rgba(244,114,182,0.35),
      rgba(139,92,246,0.4),rgba(168,85,247,0.4));
  filter:blur(80px);animation:crystal 20s linear infinite;
  opacity:0.85}
@keyframes crystal{
  0%{transform:rotate(0deg) scale(1)}
  50%{transform:rotate(180deg) scale(1.15)}
  100%{transform:rotate(360deg) scale(1)}
}

/* شبكة بلورية */
body::after{content:"";position:fixed;inset:0;z-index:-1;
  background-image:
    linear-gradient(rgba(168,85,247,0.12) 1px,transparent 1px),
    linear-gradient(90deg,rgba(34,211,238,0.12) 1px,transparent 1px),
    radial-gradient(circle at 25% 25%,rgba(251,191,36,0.15) 0%,transparent 25%),
    radial-gradient(circle at 75% 75%,rgba(244,114,182,0.15) 0%,transparent 25%);
  background-size:60px 60px,60px 60px,100% 100%,100% 100%;
  mask-image:radial-gradient(circle at center,black 30%,transparent 90%);
  animation:gridmove 30s linear infinite}
@keyframes gridmove{
  0%{background-position:0 0,0 0,0 0,0 0}
  100%{background-position:60px 60px,60px 60px,0 0,0 0}
}

.glass{background:var(--card);backdrop-filter:blur(24px) saturate(180%);
  -webkit-backdrop-filter:blur(24px) saturate(180%);
  border:1px solid var(--border);border-radius:20px;
  box-shadow:
    0 8px 40px rgba(168,85,247,0.25),
    0 0 30px rgba(34,211,238,0.15),
    inset 0 1px 0 rgba(255,255,255,0.1)}

.btn{position:relative;display:inline-flex;align-items:center;
  justify-content:center;gap:8px;padding:12px 22px;border-radius:14px;
  border:1px solid var(--border);
  background:linear-gradient(135deg,var(--c1),var(--c5),var(--c6));
  background-size:200% 200%;
  color:#fff;font-weight:700;cursor:pointer;font-family:inherit;
  font-size:15px;overflow:hidden;
  transition:transform .25s cubic-bezier(.2,.8,.2,1),box-shadow .25s;
  box-shadow:0 4px 25px rgba(168,85,247,0.5);
  animation:gradientShift 4s ease infinite}
@keyframes gradientShift{
  0%,100%{background-position:0% 50%}
  50%{background-position:100% 50%}}
.btn:hover{transform:translateY(-2px);
  box-shadow:0 8px 40px rgba(168,85,247,0.8),
             0 0 20px rgba(34,211,238,0.5)}
.btn::after{content:"";position:absolute;inset:0;
  background:linear-gradient(120deg,transparent 30%,
    rgba(255,255,255,0.4) 50%,transparent 70%);
  transform:translateX(-100%);transition:transform .7s}
.btn:hover::after{transform:translateX(100%)}

.input,textarea,select{width:100%;padding:12px 14px;border-radius:12px;
  background:rgba(11,8,32,0.75);border:1px solid var(--border);
  color:var(--text);font-family:inherit;font-size:15px;outline:none;
  transition:border-color .2s,box-shadow .2s,background .2s}
.input:focus,textarea:focus,select:focus{
  border-color:var(--c2);
  box-shadow:0 0 0 3px rgba(34,211,238,0.25),
             0 0 20px rgba(34,211,238,0.3);
  background:rgba(11,8,32,0.9)}

.topbar{position:sticky;top:0;z-index:20;padding:14px 20px;
  display:flex;align-items:center;justify-content:space-between;
  background:rgba(5,3,15,0.8);backdrop-filter:blur(20px);
  border-bottom:1px solid var(--border);
  box-shadow:0 4px 30px rgba(168,85,247,0.15)}
.brand{font-weight:800;font-size:20px;letter-spacing:2px;
  background:linear-gradient(90deg,var(--c1),var(--c2),var(--c3),var(--c4));
  background-size:300% 100%;-webkit-background-clip:text;
  background-clip:text;color:transparent;
  animation:shine 6s linear infinite;
  filter:drop-shadow(0 0 12px rgba(168,85,247,0.6))}
@keyframes shine{0%{background-position:0% 50%}100%{background-position:300% 50%}}

.muted{color:var(--muted)}
.chip{display:inline-block;padding:5px 12px;border-radius:999px;
  background:rgba(168,85,247,0.2);border:1px solid var(--border);
  color:var(--muted);font-size:12px;letter-spacing:.5px}
.grid{display:grid;gap:16px}
.g2{grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}
.pulse{animation:pulse 2s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.7}}
'''
w("static/css/main.css", CSS)

# ═══════════════════════════════════════════════════════════
# 3) choice.html — الواجهة المتبلورة
# ═══════════════════════════════════════════════════════════
CHOICE = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — وكيل الذكاء الاصطناعي الإبداعي</title>
<link rel="stylesheet" href="/static/css/main.css">
<style>
.hero{text-align:center;padding:80px 20px 30px;position:relative}
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
.card::before{content:"";position:absolute;top:-50%;left:-50%;
  width:200%;height:200%;
  background:conic-gradient(from 0deg,
    transparent,var(--c1),transparent,var(--c2),
    transparent,var(--c3),transparent);
  opacity:0;transition:opacity .5s;
  animation:rotate 8s linear infinite}
@keyframes rotate{to{transform:rotate(360deg)}}
.card:hover::before{opacity:.15}
.card .icon{font-size:28px;color:var(--c2);margin-bottom:16px;
  display:flex;align-items:center;gap:10px;
  filter:drop-shadow(0 0 8px var(--c2))}
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
    <div class="icon">&#10022; <span class="num">01</span></div>
    <h3>الواجهة الإبداعية</h3>
    <p>تحدّث بالصوت أو الكتابة. الوكيل يفهمك ويجيبك بصوت بشري.</p>
  </a>
  <a class="card" href="/studio">
    <div class="icon">&#9670; <span class="num">02</span></div>
    <h3>الاستوديو</h3>
    <p>توليد صور، فيديو، نصوص، شعارات، وهويات بصرية.</p>
  </a>
  <a class="card" href="/gallery">
    <div class="icon">&#10070; <span class="num">03</span></div>
    <h3>معرض الأعمال</h3>
    <p>كل ما أنشأته محفوظ هنا.</p>
  </a>
  <a class="card" href="/apk">
    <div class="icon">&#9635; <span class="num">04</span></div>
    <h3>بناء APK</h3>
    <p>حوّل المشروع إلى تطبيق أندرويد جاهز عبر GitHub Actions.</p>
  </a>
  <a class="card" href="/vault/hg2026">
    <div class="icon">&#9672; <span class="num">05</span></div>
    <h3>لوحة التحكم</h3>
    <p>إدارة مفاتيح API والإحصائيات.</p>
  </a>
  <a class="card" href="/docs">
    <div class="icon">&#9656; <span class="num">06</span></div>
    <h3>توثيق API</h3>
    <p>المسارات التفاعلية الكاملة.</p>
  </a>
</div>
<div class="foot">
  Hussein Ghallab <span class="sym">&#10022;</span> AL-KHALLAQI v1.0
</div>
</body>
</html>
'''
w("templates/choice.html", CHOICE)

# ═══════════════════════════════════════════════════════════
# 4) creative.html — محادثة صوتية كاملة
# ═══════════════════════════════════════════════════════════
CREATIVE = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — الواجهة الإبداعية</title>
<link rel="stylesheet" href="/static/css/main.css">
<style>
.wrap{max-width:900px;margin:0 auto;padding:16px}
.toolbar{display:flex;gap:8px;overflow-x:auto;padding:10px 0;
  scrollbar-width:none}
.toolbar::-webkit-scrollbar{display:none}
.tool{padding:9px 16px;border-radius:12px;border:1px solid var(--border);
  background:rgba(11,8,32,0.6);color:var(--muted);cursor:pointer;
  white-space:nowrap;font-weight:600;font-size:14px;transition:.25s;
  font-family:inherit}
.tool:hover,.tool.active{background:linear-gradient(135deg,var(--c1),var(--c5));
  color:#fff;border-color:transparent;
  box-shadow:0 0 20px rgba(168,85,247,0.5)}
.chat{display:flex;flex-direction:column;gap:14px;margin:16px 0;
  min-height:55vh;max-height:68vh;overflow-y:auto;padding:10px;
  scroll-behavior:smooth;border-radius:16px;
  background:rgba(5,3,15,0.4);border:1px solid var(--border)}
.chat::-webkit-scrollbar{width:6px}
.chat::-webkit-scrollbar-track{background:rgba(30,27,75,0.3);
  border-radius:3px}
.chat::-webkit-scrollbar-thumb{background:linear-gradient(180deg,
  var(--c1),var(--c2));border-radius:3px}
.msg{padding:14px 18px;border-radius:18px;max-width:85%;line-height:1.8;
  animation:rise .35s cubic-bezier(.2,.8,.2,1);word-wrap:break-word;
  position:relative}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
.msg.user{align-self:flex-start;
  background:linear-gradient(135deg,var(--c1),var(--c5));color:#fff;
  box-shadow:0 6px 30px rgba(168,85,247,0.5)}
.msg.bot{align-self:flex-end;
  background:rgba(30,27,75,0.75);border:1px solid var(--border);
  backdrop-filter:blur(16px);
  box-shadow:0 6px 30px rgba(34,211,238,0.2)}
.msg img,.msg svg{max-width:100%;border-radius:14px;margin-top:10px;
  display:block;box-shadow:0 8px 30px rgba(0,0,0,0.5)}
.msg .voice{display:inline-flex;align-items:center;gap:6px;
  padding:6px 14px;border-radius:10px;
  background:rgba(34,211,238,0.15);color:var(--c2);font-size:13px;
  cursor:pointer;margin-top:10px;border:1px solid var(--border);
  font-weight:600;transition:.2s}
.msg .voice:hover{background:rgba(34,211,238,0.3);
  box-shadow:0 0 15px rgba(34,211,238,0.5)}
.composer{position:sticky;bottom:0;padding:14px 0;
  background:linear-gradient(to top,rgba(5,3,15,0.98),transparent)}
.composer-inner{display:flex;gap:10px;align-items:flex-end}
textarea#inp{resize:none;min-height:52px;max-height:200px;line-height:1.5}
.btn-icon{width:54px;height:54px;border-radius:50%;padding:0;font-size:22px;
  display:flex;align-items:center;justify-content:center;flex-shrink:0}
.recording{background:linear-gradient(135deg,#ef4444,#dc2626)!important;
  animation:recpulse 1s infinite}
@keyframes recpulse{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,0.8)}
  50%{box-shadow:0 0 0 16px rgba(239,68,68,0)}}
</style>
</head>
<body>
<div class="topbar">
  <span class="brand">AL-KHALLAQI</span>
  <span class="chip" id="tool-label">صور</span>
</div>
<div class="wrap">
  <div class="toolbar" id="tools">
    <button class="tool active" data-t="image">&#10022; صور</button>
    <button class="tool" data-t="video">&#9670; فيديو</button>
    <button class="tool" data-t="text">&#10070; نصوص</button>
    <button class="tool" data-t="logo">&#9672; شعار</button>
    <button class="tool" data-t="identity">&#9671; هوية</button>
    <button class="tool" data-t="chat">&#10038; محادثة</button>
    <button class="tool" data-t="agent">&#9733; وكيل</button>
  </div>
  <div class="chat" id="chat">
    <div class="msg bot">
      أهلاً بك في <b style="color:var(--c2)">AL-KHALLAQI</b>
      <br>اكتب أو اضغط زر الصوت &#9673; للتحدث معي. سأجيبك بصوت بشري.
    </div>
  </div>
  <div class="composer">
    <div class="composer-inner">
      <button class="btn btn-icon" id="mic" title="تحدث معي">&#9673;</button>
      <textarea id="inp" placeholder="اكتب رسالتك أو اضغط المايك..."></textarea>
      <button class="btn btn-icon" id="send" title="إرسال">&#9656;</button>
    </div>
  </div>
</div>
<script>
const chat=document.getElementById('chat');
const inp=document.getElementById('inp');
const send=document.getElementById('send');
const mic=document.getElementById('mic');
const toolLabel=document.getElementById('tool-label');
let currentTool='image';
let sessionId=localStorage.getItem('hk_session')||('s_'+Date.now());
localStorage.setItem('hk_session', sessionId);

// ─── النزول التلقائي ───
function scrollDown(){
  requestAnimationFrame(()=>{
    chat.scrollTop=chat.scrollHeight+1000;
  });
}

// ─── الصوت البشري ───
const synth=window.speechSynthesis;
let arabicVoice=null;
function pickVoice(){
  const voices=synth.getVoices();
  arabicVoice=voices.find(v=>v.lang&&v.lang.startsWith('ar'))
    ||voices.find(v=>v.name&&v.name.includes('Arabic'))
    ||voices.find(v=>v.lang&&v.lang.startsWith('en-US'))
    ||voices[0];
}
if(synth){pickVoice();synth.onvoiceschanged=pickVoice;}
function speak(text){
  if(!synth||!text) return;
  synth.cancel();
  const u=new SpeechSynthesisUtterance(text);
  u.lang='ar-SA';
  u.rate=0.95;
  u.pitch=1.05;
  u.volume=1;
  if(arabicVoice) u.voice=arabicVoice;
  synth.speak(u);
}

// ─── الإدخال الصوتي ───
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
let recognition=null;
let isRecording=false;
if(SR){
  recognition=new SR();
  recognition.lang='ar-SA';
  recognition.continuous=false;
  recognition.interimResults=true;
  recognition.onresult=e=>{
    const txt=Array.from(e.results).map(r=>r[0].transcript).join('');
    inp.value=txt;
    if(e.results[e.results.length-1].isFinal){
      mic.classList.remove('recording');
      isRecording=false;
      setTimeout(doSend, 300);
    }
  };
  recognition.onerror=e=>{
    mic.classList.remove('recording');
    isRecording=false;
    console.warn('mic error:', e.error);
    if(e.error==='not-allowed'){
      alert('يجب السماح بالوصول للميكروفون');
    }
  };
  recognition.onend=()=>{
    mic.classList.remove('recording');
    isRecording=false;
  };
}
mic.addEventListener('click',()=>{
  if(!SR){
    alert('المتصفح لا يدعم الإدخال الصوتي. استخدم Chrome.');
    return;
  }
  if(isRecording){
    try{recognition.stop();}catch(e){}
    mic.classList.remove('recording');
    isRecording=false;
  }else{
    try{
      recognition.start();
      mic.classList.add('recording');
      isRecording=true;
    }catch(e){
      console.warn(e);
    }
  }
});

// ─── تاريخ المحادثة ───
async function loadHistory(){
  try{
    const r=await fetch('/api/v1/chat/history/'+sessionId);
    const d=await r.json();
    if(d.messages&&d.messages.length){
      chat.innerHTML='';
      d.messages.forEach(m=>{
        if(m.role==='user'){
          addMsg('user', m.content);
        }else{
          const el=addMsg('bot', m.content.replace(/\n/g,'<br>'));
          const btn=document.createElement('span');
          btn.className='voice';
          btn.innerHTML='&#9654; استماع';
          btn.onclick=()=>speak(m.content);
          el.appendChild(btn);
        }
      });
      scrollDown();
    }
  }catch(e){console.warn(e);}
}
loadHistory();

// ─── الأدوات ───
document.querySelectorAll('.tool').forEach(t=>{
  t.addEventListener('click',()=>{
    document.querySelectorAll('.tool').forEach(x=>x.classList.remove('active'));
    t.classList.add('active');
    currentTool=t.dataset.t;
    toolLabel.textContent=t.textContent.trim().replace(/^[^\s]+\s/,'');
    inp.placeholder={
      image:'صف الصورة...',video:'صف الفيديو...',text:'اكتب الموضوع...',
      logo:'اسم العلامة...',identity:'اسم المشروع...',
      chat:'تحدث معي عن أي شيء...',agent:'اكتب هدفاً كاملاً...'
    }[currentTool]||'اكتب...';
  });
});

function addMsg(cls,html){
  const d=document.createElement('div');
  d.className='msg '+cls;
  d.innerHTML=html;
  chat.appendChild(d);
  scrollDown();
  return d;
}

inp.addEventListener('input',()=>{
  inp.style.height='auto';
  inp.style.height=Math.min(inp.scrollHeight,200)+'px';
});
inp.addEventListener('keydown',e=>{
  if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();doSend();}
});

async function api(path,body){
  const r=await fetch('/api/v1'+path,{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(body)});
  if(!r.ok) throw new Error(await r.text());
  return r.json();
}

function addListenBtn(el, text){
  const btn=document.createElement('span');
  btn.className='voice';
  btn.innerHTML='&#9654; استماع';
  btn.onclick=()=>speak(text);
  el.appendChild(btn);
}

async function doSend(){
  const v=inp.value.trim();
  if(!v) return;
  inp.value='';inp.style.height='52px';
  addMsg('user', v);
  const bot=addMsg('bot','<span class="pulse">جارٍ المعالجة...</span>');
  try{
    if(currentTool==='image'){
      const d=await api('/creative/image',{prompt:v});
      bot.innerHTML='<b style="color:var(--c2)">صورة مولّدة</b><br>'
        +'<span class="muted">'+d.prompt+'</span><img src="'+d.url+'"/>';
    } else if(currentTool==='video'){
      bot.innerHTML='<span class="pulse">جارٍ توليد الفيديو...</span>';
      const d=await api('/creative/video',{prompt:v,duration:4,frames:8});
      if(d.gif){
        bot.innerHTML='<b style="color:var(--c2)">فيديو</b>'
          +'<img src="'+d.gif+'"/>';
      }else{
        bot.innerHTML='<b style="color:var(--c2)">فيديو (إطارات)</b><br>'
          +d.frames.map(u=>'<img style="max-width:150px;margin:4px" src="'+u+'"/>').join('');
      }
    } else if(currentTool==='text'){
      const d=await api('/creative/text',{prompt:v,kind:'article'});
      bot.innerHTML='<b style="color:var(--c2)">نص مولّد</b><br>'
        +d.text.replace(/\n/g,'<br>');
      addListenBtn(bot, d.text);
    } else if(currentTool==='logo'){
      const d=await api('/studio/logo',{brand:v});
      bot.innerHTML='<b style="color:var(--c2)">شعار</b><br>'+d.svg;
    } else if(currentTool==='identity'){
      const d=await api('/studio/identity',{brand:v});
      const pal=(d.palette||[]).map(c=>
        '<span style="display:inline-block;width:28px;height:28px;border-radius:8px;background:'+c+';margin:3px;box-shadow:0 0 15px '+c+'"></span>').join('');
      bot.innerHTML='<b style="color:var(--c2)">هوية بصرية</b><br>'
        +'<b>'+d.brand+'</b><br><i>'+(d.tagline||'')+'</i><br>'+pal
        +'<br>'+(d.logo_svg||'');
    } else if(currentTool==='chat'){
      const d=await api('/chat',{message:v,session_id:sessionId});
      bot.innerHTML=d.reply.replace(/\n/g,'<br>');
      addListenBtn(bot, d.reply);
      speak(d.reply);
      scrollDown();
      return;
    } else if(currentTool==='agent'){
      const d=await api('/agent/run',{goal:v,max_steps:6});
      let html='<b style="color:var(--c2)">نتيجة الوكيل</b><br>';
      (d.steps||[]).forEach(s=>{
        html+='<div style="margin:8px 0;padding:10px;'
          +'border-right:3px solid var(--c1);'
          +'background:rgba(168,85,247,0.08);border-radius:8px">'
          +'<b>خطوة '+s.step+'</b> <span class="muted">'+s.action+'</span><br>'
          +'<span>'+s.thought+'</span></div>';
      });
      html+='<hr style="border-color:var(--border);margin:12px 0">'
        +'<b>الإجابة:</b><br>'+d.final_answer;
      bot.innerHTML=html;
      addListenBtn(bot, d.final_answer);
    }
    scrollDown();
    fetch('/api/v1/chat',{method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:v,session_id:sessionId})}).catch(()=>{});
  }catch(e){
    bot.innerHTML='<b style="color:#f87171">خطأ</b><br>'+e.message;
  }
  scrollDown();
}
send.addEventListener('click',doSend);
</script>
</body>
</html>
'''
w("templates/creative.html", CREATIVE)

# ═══════════════════════════════════════════════════════════
# 5) admin.html — لوحة تحكم + API Keys
# ═══════════════════════════════════════════════════════════
ADMIN = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AL-KHALLAQI — لوحة التحكم</title>
<link rel="stylesheet" href="/static/css/main.css">
<style>
.wrap{max-width:900px;margin:0 auto;padding:22px}
.section{padding:24px;border-radius:20px;margin-bottom:20px;
  background:var(--card);border:1px solid var(--border);
  backdrop-filter:blur(20px)}
.section h3{color:var(--c1);margin-bottom:16px;letter-spacing:1px;
  display:flex;align-items:center;gap:10px}
.section h3 .sym{color:var(--c2)}
.stat{padding:20px;border-radius:16px;background:rgba(11,8,32,0.6);
  border:1px solid var(--border);margin-bottom:10px}
.stat b{font-size:30px;display:block;
  background:linear-gradient(90deg,var(--c1),var(--c2));
  -webkit-background-clip:text;background-clip:text;color:transparent}
.stat .lbl{color:var(--muted);font-size:12px;letter-spacing:1px;margin-top:6px}
.key{padding:14px;border-radius:12px;background:rgba(11,8,32,0.7);
  border:1px solid var(--border);margin:8px 0;
  font-family:monospace;font-size:13px;color:var(--c2);
  word-break:break-all;position:relative}
.key .name{color:var(--muted);font-size:11px;
  letter-spacing:1px;margin-bottom:6px;font-family:sans-serif}
.key .copy{position:absolute;top:10px;left:10px;padding:4px 10px;
  background:rgba(34,211,238,0.15);border-radius:6px;cursor:pointer;
  font-size:11px;color:var(--c2);border:1px solid var(--border);
  font-family:sans-serif}
.key .copy:hover{background:rgba(34,211,238,0.3)}
h2{color:var(--c1);margin-bottom:22px;letter-spacing:2px}
</style>
</head>
<body>
<div class="topbar">
  <span class="brand">AL-KHALLAQI</span>
  <span class="chip">لوحة التحكم</span>
</div>
<div class="wrap">
  <h2>لوحة التحكم</h2>

  <div class="section">
    <h3><span class="sym">&#9672;</span> الدخول</h3>
    <div style="display:flex;gap:10px">
      <input class="input" id="pwd" type="password" placeholder="كلمة المرور">
      <button class="btn" onclick="login()">دخول</button>
    </div>
  </div>

  <div id="panel" style="display:none">
    <div class="section">
      <h3><span class="sym">&#10022;</span> الإحصائيات</h3>
      <div class="grid g2" id="stats"></div>
    </div>

    <div class="section">
      <h3><span class="sym">&#10038;</span> إنشاء مفتاح API</h3>
      <div style="display:flex;gap:10px;margin-bottom:14px">
        <input class="input" id="keyName" placeholder="اسم المفتاح (مثلاً: تطبيقي)">
        <button class="btn" onclick="createKey()">إنشاء</button>
      </div>
      <div id="keysList"></div>
    </div>
  </div>
</div>
<script>
let pwd='';

async function login(){
  pwd=document.getElementById('pwd').value;
  if(!pwd){alert('أدخل كلمة المرور');return;}
  try{
    const r=await fetch('/api/v1/admin/stats',
      {headers:{'X-Admin-Password':pwd}});
    if(!r.ok){alert('كلمة مرور خاطئة');return;}
    const d=await r.json();
    document.getElementById('panel').style.display='block';
    renderStats(d);
    loadKeys();
  }catch(e){alert('خطأ: '+e.message);}
}

function renderStats(d){
  const out=document.getElementById('stats');
  let html='<div class="stat"><b>'+d.total_works+'</b>'
    +'<span class="lbl">إجمالي الأعمال</span></div>';
  Object.entries(d.providers||{}).forEach(([k,v])=>{
    html+='<div class="stat"><b>'+(v?'&#9679;':'&#9675;')+'</b>'
      +'<span class="lbl">'+k+'</span></div>';
  });
  Object.entries(d.by_kind||{}).forEach(([k,v])=>{
    html+='<div class="stat"><b>'+v+'</b><span class="lbl">'+k+'</span></div>';
  });
  out.innerHTML=html;
}

async function createKey(){
  const name=document.getElementById('keyName').value.trim()||'api-key';
  try{
    const r=await fetch('/api/v1/apikeys/create?name='+encodeURIComponent(name),
      {method:'POST',headers:{'X-Admin-Password':pwd}});
    const d=await r.json();
    if(d.key){
      alert('تم إنشاء المفتاح:\n\n'+d.key+'\n\nاحفظه في مكان آمن.');
      loadKeys();
    }else{
      alert('خطأ: '+(d.detail||d.error||'فشل'));
    }
  }catch(e){alert('خطأ: '+e.message);}
}

async function loadKeys(){
  try{
    const r=await fetch('/api/v1/apikeys/list',
      {headers:{'X-Admin-Password':pwd}});
    const d=await r.json();
    const out=document.getElementById('keysList');
    if(!d.keys||!d.keys.length){
      out.innerHTML='<div class="muted" style="text-align:center;padding:20px">'
        +'لا توجد مفاتيح بعد</div>';
      return;
    }
    out.innerHTML=d.keys.map(k=>
      '<div class="key"><div class="name">'+k.name+'</div>'
      +k.key
      +'<span class="copy" onclick="copyKey(\''+k.key+'\')">نسخ</span>'
      +'</div>').join('');
  }catch(e){console.warn(e);}
}

function copyKey(k){
  navigator.clipboard.writeText(k);
  alert('تم النسخ');
}
</script>
</body>
</html>
'''
w("templates/admin.html", ADMIN)

# ═══════════════════════════════════════════════════════════
# 6) inline_templates.py — نسخ مصغرة داخل بايثون
# ═══════════════════════════════════════════════════════════
lines = ['# Auto-generated. لا تعدّل يدوياً.', '']
lines.append('CSS = ' + repr(CSS))
lines.append('')
lines.append('TEMPLATES = {')
for name, html in [('choice.html', CHOICE), ('creative.html', CREATIVE),
                    ('admin.html', ADMIN)]:
    lines.append(f'    {name!r}: {html!r},')
lines.append('}')
w("app/inline_templates.py", "\n".join(lines))

# ═══════════════════════════════════════════════════════════
# 7) تأكد أن main.py يستخدم inline_templates
# ═══════════════════════════════════════════════════════════
main_path = BASE / "app" / "main.py"
src = main_path.read_text(encoding="utf-8")

# أضف import إذا ناقص
if "from app import inline_templates" not in src:
    src = src.replace(
        "from app.db.redis import close_cache",
        "from app.db.redis import close_cache\nfrom app import inline_templates"
    )

# استبدل _render بنسخة hybrid
import re
pattern = re.compile(
    r"def _render\(name: str, request: Request, \*\*kw\):.*?(?=\n@app\.get|\Z)",
    re.DOTALL
)
NEW_RENDER = '''def _render(name: str, request: Request, **kw):
    """Render مع fallback داخلي."""
    try:
        if TEMPLATES_DIR.exists() and (TEMPLATES_DIR / name).exists():
            return templates.TemplateResponse(
                name, {"request": request, "settings": settings, **kw})
    except Exception as e:
        log.warning("fs render failed for %s: %s", name, e)
    if name in inline_templates.TEMPLATES:
        log.info("using inline: %s", name)
        return HTMLResponse(inline_templates.TEMPLATES[name])
    return HTMLResponse(
        f"<html><body style='background:#05030f;color:#f5f3ff;"
        f"font-family:sans-serif;padding:40px;text-align:center'>"
        f"<h1 style='color:#a855f7'>{settings.APP_NAME}</h1>"
        f"<p>الصفحة ({name}) غير متوفرة. "
        f"<a style='color:#22d3ee' href='/'>العودة</a></p></body></html>")


'''
if pattern.search(src):
    src = pattern.sub(NEW_RENDER, src)
    print("[+] main.py (_render محدّث)")

# أضف مسارات لوحة التحكم إذا ناقصة
if "/vault/{secret}" not in src:
    src = src.rstrip() + '''

@app.get("/vault/{secret}", response_class=HTMLResponse)
async def vault(secret: str, request: Request):
    if secret != "hg2026":
        return HTMLResponse("<h1>404</h1>", status_code=404)
    return _render("admin.html", request)

@app.get("/control-panel", response_class=HTMLResponse)
async def control_panel(request: Request):
    return _render("admin.html", request)

@app.get("/apk", response_class=HTMLResponse)
async def apk_page(request: Request):
    return _render("apk.html", request)
'''
    print("[+] main.py (مسارات لوحة التحكم)")

main_path.write_text(src, encoding="utf-8")

# ═══════════════════════════════════════════════════════════
# 8) رفع
# ═══════════════════════════════════════════════════════════
print()
print("=" * 60)
print("  اكتمل كل شيء")
print("=" * 60)
print()
print("  ✓ CSS جديد: بلورات كريستالية متحركة")
print("  ✓ choice.html: واجهة متبلورة من المستقبل")
print("  ✓ creative.html: محادثة صوتية كاملة")
print("  ✓ admin.html: لوحة تحكم + API keys")
print("  ✓ inline_templates: نسخ مصغرة مضمونة")
print("  ✓ main.py: /vault/hg2026 + /control-panel")
print()
print("ارفع:")
print("   git add -A")
print('   git commit -m "Force new crystal UI + voice + API keys"')
print("   git push origin main")
print("=" * 60)
