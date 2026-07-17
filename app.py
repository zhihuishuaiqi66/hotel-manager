"""
小陈家·环洱度假美宿 酒店管理系统
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import urllib.request
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Firebase Realtime Database 配置
FIREBASE_URL = "https://hotel-manager-e5c77-default-rtdb.firebaseio.com"

ROOMS = ['101', '201', '202', '203', '204', '205', '301', '302', '303', '304', '305', '306']

def load_firebase_data(path, default=None):
    """从Firebase加载数据"""
    if default is None:
        default = []
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data is None:
                return default
            if isinstance(data, dict):
                return list(data.values())
            return data
    except Exception as e:
        print(f"Error loading from Firebase: {e}")
        return default

def save_firebase_data(path, data):
    """保存数据到Firebase"""
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=payload, method='PUT')
        req.add_header('Content-Type', 'application/json')
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print(f"Error saving to Firebase: {e}")
        return False

ROOMS = ['101', '201', '202', '203', '204', '205', '301', '302', '303', '304', '305', '306']

# ==================== 早餐页面 ====================
BREAKFAST_HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>早餐预订</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        :root{--s:#9CAF88;--sd:#7A9568;--n:#1A2A4A;--c:#FAF8F5;--g:#C9A961;--w:#fff}
        body{font-family:-apple-system,'Noto Sans SC',sans-serif;background:linear-gradient(135deg,#2a3f5f 0%,#1a2a4a 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;animation:fadeIn .5s ease}
        @keyframes fadeIn{from{opacity:0}to{opacity:1}}
        @keyframes slideUp{from{opacity:0;transform:translateY(30px) scale(.95)}to{opacity:1;transform:translateY(0) scale(1)}}
        @keyframes fadeInUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
        @keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}
        @keyframes checkPop{0%{transform:scale(0)}50%{transform:scale(1.2)}100%{transform:scale(1)}}
        .modal{background:var(--w);border-radius:24px;padding:32px 28px;width:100%;max-width:420px;max-height:90vh;overflow-y:auto;position:relative;animation:slideUp .4s cubic-bezier(.4,0,.2,1);box-shadow:0 20px 60px rgba(0,0,0,.3)}
        .modal::-webkit-scrollbar{width:6px}
        .modal::-webkit-scrollbar-thumb{background:#ddd;border-radius:3px}
        .close{position:absolute;top:16px;right:16px;width:36px;height:36px;background:#f5f5f5;border:none;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;z-index:10}
        .close:hover{background:#e0e0e0;transform:rotate(90deg)}
        .close svg{width:18px;height:18px;stroke:#999;stroke-width:2;fill:none}
        .title{font-size:1.4rem;font-weight:700;color:var(--n);margin-bottom:6px}
        .subtitle{font-size:.9rem;color:#888;margin-bottom:24px}
        .section{margin-bottom:24px;animation:fadeInUp .4s ease}
        .section-title{font-size:.85rem;color:#666;margin-bottom:12px;font-weight:600;display:flex;align-items:center;gap:8px}
        .section-title::before{content:'';width:4px;height:14px;background:linear-gradient(135deg,var(--s),var(--sd));border-radius:2px}
        .rooms{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
        .room-btn{padding:14px 8px;border:2px solid #e8e2d8;border-radius:12px;background:linear-gradient(135deg,var(--w) 0%,#f8f6f3 100%);font-size:1rem;font-weight:600;cursor:pointer;transition:all .3s;text-align:center;font-family:inherit}
        .room-btn:hover{border-color:var(--s);transform:translateY(-2px);box-shadow:0 4px 12px rgba(156,175,136,.3)}
        .room-btn.selected{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border-color:var(--s);animation:pulse .3s ease;box-shadow:0 4px 16px rgba(156,175,136,.4)}
        .qty-section{background:#f8f6f3;border-radius:14px;padding:20px;margin-top:16px}
        .qty-label{font-size:.85rem;color:#888;margin-bottom:12px}
        .qty-row{display:flex;align-items:center;justify-content:center;gap:24px}
        .qbtn{width:44px;height:44px;border-radius:50%;border:none;background:var(--w);font-size:1.4rem;cursor:pointer;transition:all .2s;box-shadow:0 2px 8px rgba(0,0,0,.1);display:flex;align-items:center;justify-content:center;font-family:inherit;color:var(--n)}
        .qbtn:hover{transform:scale(1.1);box-shadow:0 4px 12px rgba(0,0,0,.15)}
        .qbtn:active{transform:scale(0.95)}
        .qnum{font-size:2.2rem;font-weight:700;color:var(--n);min-width:50px;text-align:center}
        .bowl{background:#f8f6f3;border-radius:14px;padding:18px;margin-bottom:14px;border-left:4px solid var(--g);animation:fadeInUp .4s ease}
        .bowl-header{display:flex;align-items:center;gap:10px;margin-bottom:14px}
        .bowl-num{width:28px;height:28px;background:linear-gradient(135deg,var(--g),#b89a4a);border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:.75rem;font-weight:600}
        .bowl-title{font-size:.95rem;font-weight:600;color:var(--n)}
        .opt-group{display:flex;flex-direction:column;gap:10px}
        .opt-row{display:flex;align-items:center;gap:10px}
        .opt-label{font-size:.8rem;color:#999;width:40px;flex-shrink:0;font-weight:500}
        .opt-btns{display:flex;gap:8px;flex:1}
        .obtn{flex:1;padding:10px;border:2px solid #e8e2d8;border-radius:8px;background:var(--w);font-size:.85rem;cursor:pointer;transition:all .3s;text-align:center;font-family:inherit;font-weight:500}
        .obtn:hover{border-color:var(--s)}
        .obtn.sel{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border-color:var(--s)}
        .submit{width:100%;padding:16px;background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border:none;border-radius:12px;font-size:1rem;font-weight:600;cursor:pointer;transition:all .3s;font-family:inherit;opacity:.5;margin-top:8px}
        .submit.active{opacity:1}
        .submit.active:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(156,175,136,.4)}
        .immediate-btn{background:linear-gradient(135deg,var(--g),#b89a4a);margin-top:12px;opacity:1}
        .immediate-btn:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(201,169,97,.4)}
        .popup-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.5);display:none;align-items:center;justify-content:center;z-index:1000;animation:fadeIn .3s ease}
        .popup-overlay.show{display:flex}
        .popup-card{background:#fff;border-radius:20px;padding:32px;max-width:320px;text-align:center;animation:slideUp .4s ease}
        .popup-icon{font-size:3rem;margin-bottom:16px}
        .popup-title{font-size:1.2rem;font-weight:700;color:var(--n);margin-bottom:8px}
        .popup-msg{font-size:.9rem;color:#666;margin-bottom:20px;line-height:1.6}
        .popup-btn{padding:12px 32px;background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border:none;border-radius:10px;font-size:1rem;cursor:pointer;font-family:inherit;font-weight:500}
        .success{text-align:center;padding:20px 0;display:none}
        .success-icon{width:72px;height:72px;background:linear-gradient(135deg,var(--s),var(--sd));border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;animation:checkPop .4s ease}
        .success svg{width:36px;height:36px;stroke:#fff;stroke-width:2;fill:none}
        .success h3{font-size:1.2rem;color:var(--n);margin-bottom:6px}
        .success p{font-size:.85rem;color:#888;margin-bottom:16px}
        .btn-outline{padding:12px 28px;background:transparent;border:2px solid var(--s);color:var(--s);border-radius:10px;cursor:pointer;font-size:.9rem;font-weight:500;transition:all .3s;font-family:inherit}
        .btn-outline:hover{background:var(--s);color:#fff}
        .form-content.hidden{display:none}
    </style>
</head>
<body>
<div class="modal">
    <button class="close" onclick="location.reload()"><svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    <div class="form-content" id="formContent">
        <div class="title">早餐预订</div>
        <div class="subtitle">小陈家·环洱度假美宿</div>
        <div class="section">
            <div class="section-title">选择房号</div>
            <div class="rooms" id="roomSel"></div>
        </div>
        <div class="section" id="qtySection" style="display:none">
            <div class="section-title">选择份数</div>
            <div class="qty-section">
                <div class="qty-label">选择需要的碗数</div>
                <div class="qty-row">
                    <button class="qbtn" onclick="changeQty(-1)">−</button>
                    <span class="qnum" id="qty">1</span>
                    <button class="qbtn" onclick="changeQty(1)">+</button>
                </div>
            </div>
        </div>
        <div id="bowlArea"></div>
        <button class="submit" id="submitBtn" onclick="submitAll()" disabled>提交全部订单</button>
        <button class="submit immediate-btn" onclick="immediateOrder()">立即用餐</button>
    </div>
    <div class="success" id="successMsg">
        <div class="success-icon"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div>
        <h3>预订成功！</h3>
        <p id="resultMsg">您的早餐已记录</p>
        <button class="btn-outline" onclick="location.reload()">继续预订</button>
        <button class="btn-outline" style="margin-left:10px;background:var(--s);color:#fff" onclick="location.href='https://hotel-manager-h65n.onrender.com/'">返回首页</button>
    </div>
</div>
<div class="popup-overlay" id="popupOverlay" onclick="closePopup()">
    <div class="popup-card" onclick="event.stopPropagation()">
        <div class="popup-icon">🍳</div>
        <div class="popup-title">已收到您的订单</div>
        <div class="popup-msg">由于早餐是现点现做<br>需要等待 <strong>5-10分钟</strong><br>请在用餐区稍作等候</div>
        <button class="popup-btn" onclick="closePopup()">我知道了</button>
    </div>
</div>
<script>
const rooms=['101','201','202','203','204','205','301','302','303','304','305','306'];
let selectedRoom='',bowlCount=0,bowlData={};
document.getElementById('roomSel').innerHTML=rooms.map((r,i)=>`<button class="room-btn" onclick="selectRoom('${r}')">${r}</button>`).join('');
function selectRoom(r){selectedRoom=r;document.querySelectorAll('.room-btn').forEach(b=>b.classList.remove('selected'));event.target.classList.add('selected');document.getElementById('qtySection').style.display='block';if(bowlCount===0)changeQty(1)}
function changeQty(d){bowlCount=Math.max(1,Math.min(10,bowlCount+d));document.getElementById('qty').textContent=bowlCount;renderBowls()}
function renderBowls(){const a=document.getElementById('bowlArea');if(bowlCount===0){a.innerHTML='';checkSubmit();return}let h='';for(let i=1;i<=bowlCount;i++){const d=bowlData[i]||{};h+=`<div class="bowl"><div class="bowl-header"><div class="bowl-num">${i}</div><div class="bowl-title">第 ${i} 碗</div></div><div class="opt-group"><div class="opt-row"><span class="opt-label">汤底</span><div class="opt-btns"><button class="obtn ${d.soup==='清汤'?'sel':''}" onclick="setBowl(${i},'soup','清汤')">清汤</button><button class="obtn ${d.soup==='红油'?'sel':''}" onclick="setBowl(${i},'soup','红油')">红油</button></div></div><div class="opt-row"><span class="opt-label">葱花</span><div class="opt-btns"><button class="obtn ${d.onion==='要'?'sel':''}" onclick="setBowl(${i},'onion','要')">要</button><button class="obtn ${d.onion==='不要'?'sel':''}" onclick="setBowl(${i},'onion','不要')">不要</button></div></div><div class="opt-row"><span class="opt-label">香菜</span><div class="opt-btns"><button class="obtn ${d.herb==='要'?'sel':''}" onclick="setBowl(${i},'herb','要')">要</button><button class="obtn ${d.herb==='不要'?'sel':''}" onclick="setBowl(${i},'herb','不要')">不要</button></div></div></div></div>`}a.innerHTML=h;checkSubmit()}
function setBowl(n,k,v){if(!bowlData[n])bowlData[n]={};bowlData[n][k]=v;renderBowls()}
function checkSubmit(){let ok=selectedRoom&&bowlCount>0;for(let i=1;i<=bowlCount;i++){const d=bowlData[i]||{};if(!d.soup||!d.onion||!d.herb){ok=false;break}}const b=document.getElementById('submitBtn');b.disabled=!ok;if(ok)b.classList.add('active');else b.classList.remove('active')}
async function submitAll(){const b=document.getElementById('submitBtn');b.disabled=true;b.textContent='提交中...';let c=0;for(let i=1;i<=bowlCount;i++){const d=bowlData[i];try{await fetch('/api/breakfast',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({room:selectedRoom,...d})});c++}catch(e){}}document.getElementById('formContent').classList.add('hidden');document.getElementById('successMsg').style.display='block';document.getElementById('resultMsg').textContent=`${selectedRoom}房 ${c}碗早餐已记录`}
function immediateOrder(){document.getElementById('popupOverlay').classList.add('show')}
function closePopup(){document.getElementById('popupOverlay').classList.remove('show')}
</script>
</body></html>'''

# ==================== 客房清洁页面 ====================
CLEANING_HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>客房清洁</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        :root{--s:#9CAF88;--sd:#7A9568;--n:#1A2A4A;--c:#FAF8F5;--g:#C9A961;--r:#E53E3E;--w:#fff}
        body{font-family:-apple-system,'Noto Sans SC',sans-serif;background:linear-gradient(135deg,#2a3f5f 0%,#1a2a4a 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;animation:fadeIn .5s ease}
        @keyframes fadeIn{from{opacity:0}to{opacity:1}}
        @keyframes slideUp{from{opacity:0;transform:translateY(30px) scale(.95)}to{opacity:1;transform:translateY(0) scale(1)}}
        @keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}
        @keyframes checkPop{0%{transform:scale(0)}50%{transform:scale(1.2)}100%{transform:scale(1)}}
        .modal{background:var(--w);border-radius:24px;padding:32px 28px;width:100%;max-width:400px;max-height:90vh;overflow-y:auto;position:relative;animation:slideUp .4s cubic-bezier(.4,0,.2,1);box-shadow:0 20px 60px rgba(0,0,0,.3)}
        .modal::-webkit-scrollbar{width:6px}
        .modal::-webkit-scrollbar-thumb{background:#ddd;border-radius:3px}
        .close{position:absolute;top:16px;right:16px;width:36px;height:36px;background:#f5f5f5;border:none;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;z-index:10}
        .close:hover{background:#e0e0e0;transform:rotate(90deg)}
        .close svg{width:18px;height:18px;stroke:#999;stroke-width:2;fill:none}
        .title{font-size:1.4rem;font-weight:700;color:var(--n);margin-bottom:6px}
        .subtitle{font-size:.9rem;color:#888;margin-bottom:24px}
        .section{margin-bottom:20px}
        .section-title{font-size:.85rem;color:#666;margin-bottom:12px;font-weight:600;display:flex;align-items:center;gap:8px}
        .section-title::before{content:'';width:4px;height:14px;background:linear-gradient(135deg,var(--s),var(--sd));border-radius:2px}
        .rooms{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
        .room-btn{padding:14px 8px;border:2px solid #e8e2d8;border-radius:12px;background:linear-gradient(135deg,var(--w) 0%,#f8f6f3 100%);font-size:1rem;font-weight:600;cursor:pointer;transition:all .3s;text-align:center;font-family:inherit}
        .room-btn:hover{border-color:var(--s);transform:translateY(-2px);box-shadow:0 4px 12px rgba(156,175,136,.3)}
        .room-btn.selected{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border-color:var(--s);animation:pulse .3s ease;box-shadow:0 4px 16px rgba(156,175,136,.4)}
        .options{display:flex;flex-direction:column;gap:12px}
        .opt-card{display:flex;align-items:center;gap:16px;padding:18px;border:2px solid #e8e2d8;border-radius:14px;cursor:pointer;transition:all .3s;background:var(--w)}
        .opt-card:hover{border-color:var(--s);background:#f8faf8}
        .opt-card.selected{border-color:var(--s);background:linear-gradient(135deg,#f0f9f0 0%,#e8f5e8 100%)}
        .opt-icon{width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:1.4rem}
        .opt-card:first-child .opt-icon{background:linear-gradient(135deg,#e8f5e9 0%,#c8e6c9 100%)}
        .opt-card:last-child .opt-icon{background:linear-gradient(135deg,#f5f5f5 0%,#e0e0e0 100%)}
        .opt-text h4{font-size:1rem;font-weight:600;color:var(--n);margin-bottom:2px}
        .opt-text p{font-size:.8rem;color:#999}
        .opt-check{width:22px;height:22px;border:2px solid #ddd;border-radius:50%;margin-left:auto;display:flex;align-items:center;justify-content:center;transition:all .3s;flex-shrink:0}
        .opt-card.selected .opt-check{background:var(--s);border-color:var(--s)}
        .opt-card.selected .opt-check svg{opacity:1}
        .opt-check svg{width:12px;height:12px;stroke:#fff;stroke-width:3;fill:none;opacity:0;transition:opacity .2s}
        .time-section{margin-top:20px;padding-top:20px;border-top:1px solid #f0f0f0;display:none}
        .time-section.show{display:block}
        .time-label{font-size:.85rem;color:#666;margin-bottom:12px;font-weight:500}
        .time-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
        .time-btn{padding:12px 8px;border:2px solid #e8e2d8;border-radius:10px;background:var(--w);font-size:.85rem;cursor:pointer;transition:all .3s;text-align:center;font-family:inherit;font-weight:500}
        .time-btn:hover{border-color:var(--s)}
        .time-btn.selected{background:var(--s);color:#fff;border-color:var(--s)}
        .note-input{width:100%;padding:12px 16px;border:2px solid #e8e2d8;border-radius:10px;font-size:.9rem;font-family:inherit;transition:all .2s;margin-top:12px;resize:none}
        .note-input:focus{outline:none;border-color:var(--s);box-shadow:0 0 0 3px rgba(156,175,136,.2)}
        .submit{width:100%;padding:16px;background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border:none;border-radius:12px;font-size:1rem;font-weight:600;cursor:pointer;transition:all .3s;font-family:inherit;margin-top:20px;opacity:.5}
        .submit.active{opacity:1}
        .submit.active:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(156,175,136,.4)}
        .success{text-align:center;padding:20px 0;display:none}
        .success-icon{width:72px;height:72px;background:linear-gradient(135deg,var(--s),var(--sd));border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;animation:checkPop .4s ease}
        .success svg{width:36px;height:36px;stroke:#fff;stroke-width:2;fill:none}
        .success h3{font-size:1.2rem;color:var(--n);margin-bottom:6px}
        .success p{font-size:.85rem;color:#888}
        .form-content.hidden{display:none}
    </style>
</head>
<body>
<div class="modal">
    <button class="close" onclick="location.reload()"><svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    <div class="form-content" id="formContent">
        <div class="title">客房清洁服务</div>
        <div class="subtitle">请选择今日客房服务状态</div>
        <div class="section"><div class="section-title">选择房号</div><div class="rooms" id="roomSel"></div></div>
        <div class="section" id="optSection" style="display:none">
            <div class="section-title">服务选择</div>
            <div class="options">
                <div class="opt-card" onclick="selectOpt(this,'yes')"><div class="opt-icon">🧹</div><div class="opt-text"><h4>需要清洁</h4><p>请选择期望打扫时间</p></div><div class="opt-check"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div></div>
                <div class="opt-card" onclick="selectOpt(this,'no')"><div class="opt-icon">🚫</div><div class="opt-text"><h4>免打扰</h4><p>今日无需清洁客房</p></div><div class="opt-check"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div></div>
            </div>
        </div>
        <div class="time-section" id="timeSection">
            <div class="time-label">期望打扫时间（16点前）</div>
            <div class="time-grid">
                <button class="time-btn" onclick="selectTime(this,'8:00-9:00')">8:00-9:00</button>
                <button class="time-btn" onclick="selectTime(this,'9:00-10:00')">9:00-10:00</button>
                <button class="time-btn" onclick="selectTime(this,'10:00-11:00')">10:00-11:00</button>
                <button class="time-btn" onclick="selectTime(this,'11:00-12:00')">11:00-12:00</button>
                <button class="time-btn" onclick="selectTime(this,'13:00-14:00')">13:00-14:00</button>
                <button class="time-btn" onclick="selectTime(this,'14:00-15:00')">14:00-15:00</button>
                <button class="time-btn" onclick="selectTime(this,'15:00-16:00')">15:00-16:00</button>
            </div>
            <textarea class="note-input" id="noteInput" placeholder="备注信息（选填）" rows="2"></textarea>
        </div>
        <button class="submit" id="submitBtn" onclick="submitForm()">提交选择</button>
    </div>
    <div class="success" id="successMsg">
        <div class="success-icon"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div>
        <h3>提交成功！</h3>
        <p id="resultMsg">您的选择已记录</p>
    </div>
</div>
<script>
const rooms=['101','201','202','203','204','205','301','302','303','304','305','306'];
let selectedRoom='',selectedOpt='',selectedTime='';
document.getElementById('roomSel').innerHTML=rooms.map(r=>`<button class="room-btn" onclick="selectRoom('${r}')">${r}</button>`).join('');
function selectRoom(r){selectedRoom=r;selectedOpt='';selectedTime='';document.querySelectorAll('.room-btn').forEach(b=>b.classList.remove('selected'));event.target.classList.add('selected');document.querySelectorAll('.opt-card').forEach(c=>c.classList.remove('selected'));document.querySelectorAll('.time-btn').forEach(b=>b.classList.remove('selected'));document.getElementById('optSection').style.display='block';document.getElementById('timeSection').classList.remove('show');document.getElementById('submitBtn').classList.remove('active')}
function selectOpt(el,v){selectedOpt=v;selectedTime='';document.querySelectorAll('.opt-card').forEach(c=>c.classList.remove('selected'));el.classList.add('selected');document.querySelectorAll('.time-btn').forEach(b=>b.classList.remove('selected'));document.getElementById('timeSection').classList.toggle('show',v==='yes');checkForm()}
function selectTime(el,t){selectedTime=t;document.querySelectorAll('.time-btn').forEach(b=>b.classList.remove('selected'));el.classList.add('selected');checkForm()}
function checkForm(){document.getElementById('submitBtn').classList.toggle('active',selectedRoom&&selectedOpt&&(selectedOpt==='no'||selectedTime))}
async function submitForm(){if(!selectedRoom||!selectedOpt)return;if(selectedOpt==='yes'&&!selectedTime)return;const b=document.getElementById('submitBtn');b.textContent='提交中...';b.disabled=true;const note=document.getElementById('noteInput').value;try{await fetch('/api/cleaning',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({room:selectedRoom,need:selectedOpt,time:selectedTime,note:note})});document.getElementById('formContent').classList.add('hidden');document.getElementById('successMsg').style.display='block';document.getElementById('resultMsg').textContent=`${selectedRoom}房 ${selectedOpt==='yes'?'打扫时间：'+selectedTime:'免打扰'} 已记录`}catch(e){alert('提交失败');b.textContent='提交选择';b.disabled=false}}
</script>
</body></html>'''

# ==================== 后台管理页面 ====================
ADMIN_HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>后台管理</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        :root{--s:#9CAF88;--sd:#7A9568;--n:#1A2A4A;--c:#FAF8F5;--g:#C9A961;--r:#E53E3E}
        body{font-family:-apple-system,'Noto Sans SC',sans-serif;background:linear-gradient(135deg,#f5f0e8 0%,#e8e2d8 100%);min-height:100vh;animation:fadeIn .6s ease}
        @keyframes fadeIn{from{opacity:0}to{opacity:1}}
        @keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(72,187,120,.4)}50%{opacity:.8;box-shadow:0 0 0 8px rgba(72,187,120,0)}}
        @keyframes slideIn{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
        @keyframes checkPop{0%{transform:scale(0)}50%{transform:scale(1.2)}100%{transform:scale(1)}}
        .login-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:linear-gradient(135deg,#2a3f5f 0%,#1a2a4a 100%);display:flex;align-items:center;justify-content:center;z-index:1000}
        .login-card{background:#fff;border-radius:24px;padding:40px;width:100%;max-width:360px;text-align:center;animation:slideUp .4s ease}
        @keyframes slideUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
        .login-icon{width:80px;height:80px;background:linear-gradient(135deg,var(--s),var(--sd));border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 24px;font-size:2rem}
        .login-title{font-size:1.4rem;font-weight:700;color:var(--n);margin-bottom:8px}
        .login-subtitle{font-size:.9rem;color:#888;margin-bottom:28px}
        .login-input{width:100%;padding:16px;border:2px solid #e8e2d8;border-radius:12px;font-size:1rem;font-family:inherit;text-align:center;letter-spacing:.1em;transition:all .3s}
        .login-input:focus{outline:none;border-color:var(--s);box-shadow:0 0 0 3px rgba(156,175,136,.2)}
        .login-btn{width:100%;padding:16px;background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border:none;border-radius:12px;font-size:1rem;font-weight:600;cursor:pointer;transition:all .3s;font-family:inherit;margin-top:20px}
        .login-btn:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(156,175,136,.4)}
        .login-error{color:var(--r);font-size:.85rem;margin-top:12px;display:none}
        .admin-content{display:none}
        .admin-content.show{display:block}
        .hd{background:linear-gradient(135deg,var(--n) 0%,#0f1a2e 100%);color:#fff;padding:20px;position:sticky;top:0;z-index:100;box-shadow:0 4px 20px rgba(0,0,0,.2)}
        .hdc{max-width:900px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}
        .hd h1{font-size:1.3rem;font-weight:700;letter-spacing:.5px}
        .st{font-size:.75rem;display:flex;align-items:center;gap:8px;background:rgba(255,255,255,.15);padding:8px 16px;border-radius:20px}
        .dot{width:10px;height:10px;background:#48BB78;border-radius:50%;animation:pulse 2s infinite}
        .ct{max-width:900px;margin:0 auto;padding:24px 20px}
        .stats{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:24px}
        .stat-card{background:#fff;border-radius:16px;padding:24px;box-shadow:0 4px 20px rgba(0,0,0,.06);animation:slideIn .5s ease}
        .stat-icon{width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.5rem;margin-bottom:12px}
        .stat-card:first-child .stat-icon{background:linear-gradient(135deg,#e8f5e9 0%,#c8e6c9 100%)}
        .stat-card:last-child .stat-icon{background:linear-gradient(135deg,#fff3e0 0%,#ffe0b2 100%)}
        .stat-value{font-size:2.5rem;font-weight:700;color:var(--n)}
        .stat-label{font-size:.85rem;color:#888;margin-top:4px}
        .sec{margin-bottom:28px;animation:slideIn .5s ease}
        .sh{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
        .stl{font-size:1.1rem;color:var(--n);display:flex;align-items:center;gap:12px;font-weight:700}
        .stl::before{content:'';width:4px;height:20px;background:linear-gradient(135deg,var(--s),var(--sd));border-radius:2px}
        .bdg{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;padding:6px 16px;border-radius:20px;font-size:.8rem;font-weight:600}
        .cd{background:#fff;border-radius:20px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.06)}
        .oi{padding:16px 20px;border-bottom:1px solid #f5f5f5;display:flex;flex-wrap:wrap;align-items:center;gap:8px;font-size:.9rem}
        .oi:last-child{border-bottom:none}
        .ot{color:var(--g);font-weight:700;font-size:1rem}
        .od{color:#555;flex:1}
        .em{text-align:center;padding:60px 20px;color:#aaa;font-size:.9rem}
        .em svg{width:64px;height:64px;stroke:#ddd;stroke-width:1;fill:none;margin-bottom:16px;opacity:.5}
        .soup-tag{background:linear-gradient(135deg,#fff3e0 0%,#ffe0b2 100%);color:#e65100;padding:4px 10px;border-radius:6px;font-size:.8rem;font-weight:500}
        .onion-tag{background:linear-gradient(135deg,#e8f5e9 0%,#c8e6c9 100%);color:#2e7d32;padding:4px 10px;border-radius:6px;font-size:.8rem;font-weight:500}
        .herb-tag{background:linear-gradient(135deg,#f3e5f5 0%,#e1bee7 100%);color:#7b1fa2;padding:4px 10px;border-radius:6px;font-size:.8rem;font-weight:500}
        .done-badge{background:linear-gradient(135deg,#e3f2fd 0%,#bbdefb 100%);color:#1565c0;padding:4px 10px;border-radius:6px;font-size:.8rem;font-weight:500}
        .action-btn{padding:6px 12px;border:none;border-radius:8px;font-size:.75rem;cursor:pointer;transition:all .2s;font-family:inherit;font-weight:500;margin-left:8px}
        .action-btn.done{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff}
        .action-btn.done:hover{transform:scale(1.05)}
        .action-btn.seen{background:linear-gradient(135deg,var(--g),#b89a4a);color:#fff}
        .action-btn.seen:hover{transform:scale(1.05)}
        .action-btn.mute{background:linear-gradient(135deg,#9e9e9e,#757575);color:#fff}
        .sound-control{position:fixed;bottom:20px;right:20px;z-index:100}
        .time-badge{background:linear-gradient(135deg,#e3f2fd 0%,#bbdefb 100%);color:#1976d2;padding:4px 10px;border-radius:12px;font-size:.75rem;font-weight:500}
        .clean-badge{background:linear-gradient(135deg,#e8f5e9 0%,#c8e6c9 100%);color:#388e3c;padding:4px 10px;border-radius:12px;font-size:.75rem;font-weight:500}
        .skip-badge{background:linear-gradient(135deg,#fce4ec 0%,#f8bbd9 100%);color:#c2185b;padding:4px 10px;border-radius:12px;font-size:.75rem;font-weight:500}
        .refresh-btn{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border:none;border-radius:20px;font-size:.8rem;cursor:pointer;transition:all .3s;font-family:inherit}
        .refresh-btn:hover{transform:scale(1.05)}
        select{padding:8px 12px;border:1px solid #ddd;border-radius:8px;font-size:.85rem;font-family:inherit;cursor:pointer}
    </style>
</head>
<body>
<div class="login-overlay" id="loginOverlay">
    <div class="login-card">
        <div class="login-icon">🔐</div>
        <div class="login-title">后台管理</div>
        <div class="login-subtitle">请输入访问密码</div>
        <input type="password" class="login-input" id="loginInput" placeholder="请输入密码" onkeypress="if(event.key==='Enter')checkLogin()">
        <button class="login-btn" onclick="checkLogin()">进入后台</button>
        <div class="login-error" id="loginError">密码错误，请重试</div>
    </div>
</div>
<div class="admin-content" id="adminContent">
<div class="hd"><div class="hdc"><h1>后台管理</h1><div class="st"><div class="dot"></div><span>实时更新</span><button class="refresh-btn" onclick="refreshWithSound()">刷新</button></div></div></div>
<div class="ct">
    <div class="stats">
        <div class="stat-card"><div class="stat-icon">🍜</div><div class="stat-value" id="oc">0</div><div class="stat-label">早餐订单</div></div>
        <div class="stat-card"><div class="stat-icon">🧹</div><div class="stat-value" id="cc">0</div><div class="stat-label">清洁请求</div></div>
    </div>
    <div class="sec"><div class="sh"><div class="stl">早餐订单</div><select id="breakfastFilter" onchange="loadO()"><option value="1">今天</option><option value="3">近3天</option><option value="7" selected>近7天</option><option value="30">近30天</option></select></div><div class="cd" id="ol"><div class="em"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><p>暂无订单</p></div></div></div>
    <div class="sec"><div class="sh"><div class="stl">清洁请求</div><select id="cleaningFilter" onchange="loadC()"><option value="1">今天</option><option value="3">近3天</option><option value="7" selected>近7天</option><option value="30">近30天</option></select></div><div class="cd" id="cl"><div class="em"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><p>暂无请求</p></div></div></div>
</div>
</div>
<script>
let soundEnabled=true,lastO=0,lastC=0;
function playNotification(){if(!soundEnabled)return;try{const a=new(window.AudioContext||window.webkitAudioContext)(),o=a.createOscillator(),g=a.createGain();o.connect(g);g.connect(a.destination);o.frequency.value=800;o.type='sine';g.gain.setValueAtTime(.3,a.currentTime);g.gain.exponentialRampToValueAtTime(.01,a.currentTime+.3);o.start(a.currentTime);o.stop(a.currentTime+.3)}catch(e){}}
async function refreshWithSound(){const pO=lastO,pC=lastC;await Promise.all([loadO(),loadC()]);lastO=parseInt(document.getElementById('oc').textContent)||0;lastC=parseInt(document.getElementById('cc').textContent)||0;if(lastO>pO||lastC>pC)playNotification()}
async function loadO(){const d=document.getElementById('breakfastFilter').value;const r=await fetch(`/api/breakfast?days=${d}`);const o=await r.json();document.getElementById('oc').textContent=o.length;if(!o.length){document.getElementById('ol').innerHTML='<div class="em"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><p>暂无订单</p></div>';return}const s=[...o].sort((a,b)=>new Date(b.timestamp)-new Date(a.timestamp));document.getElementById('ol').innerHTML=s.map((x,i)=>`<div class="oi"><span class="ot">${x.room}房</span><span class="soup-tag">${x.soup}</span><span class="onion-tag">葱:${x.onion}</span><span class="herb-tag">香:${x.herb}</span>${x.status==='done'?'<span class="done-badge">已做好</span>':''}<span class="time-badge">${x.date} ${x.time}</span>${x.status!=='done'?`<button class="action-btn done" onclick="markDone('${x.timestamp}')">已做好</button>`:''}${x.status!=='seen'?`<button class="action-btn seen" onclick="markSeen('${x.timestamp}')">看到了</button>`:''}</div>`).join('')}
async function loadC(){const d=document.getElementById('cleaningFilter').value;const r=await fetch(`/api/cleaning?days=${d}`);const c=await r.json();document.getElementById('cc').textContent=c.length;if(!c.length){document.getElementById('cl').innerHTML='<div class="em"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><p>暂无请求</p></div>';return}const s=[...c].sort((a,b)=>new Date(b.timestamp)-new Date(a.timestamp));document.getElementById('cl').innerHTML=s.map((x,i)=>`<div class="oi"><span class="ot">${x.room}房</span><span class="${x.need==='yes'?'clean-badge':'skip-badge'}">${x.need==='yes'?'需要打扫':'免打扰'}</span>${x.status==='done'?'<span class="done-badge">已打扫</span>':''}<span class="time-badge">${x.date} ${x.time}</span>${x.status!=='done'?`<button class="action-btn done" onclick="markCleanDone('${x.timestamp}')">已打扫</button>`:''}${x.status!=='seen'?`<button class="action-btn seen" onclick="markCleanSeen('${x.timestamp}')">看到了</button>`:''}</div>`).join('')}
async function markDone(ts){await fetch('/api/breakfast/mark',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({timestamp:ts,status:'done'})});loadO()}
async function markSeen(ts){await fetch('/api/breakfast/mark',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({timestamp:ts,status:'seen'})});loadO()}
async function markCleanDone(ts){await fetch('/api/cleaning/mark',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({timestamp:ts,status:'done'})});loadC()}
async function markCleanSeen(ts){await fetch('/api/cleaning/mark',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({timestamp:ts,status:'seen'})});loadC()}
function checkLogin(){const i=document.getElementById('loginInput').value;if(i==='232566cc'){document.getElementById('loginOverlay').style.display='none';document.getElementById('adminContent').classList.add('show');refreshWithSound();setInterval(refreshWithSound,3000)}else{document.getElementById('loginError').style.display='block';document.getElementById('loginInput').value='';document.getElementById('loginInput').focus()}}
</script>
</body></html>'''

# ==================== 退房提醒页面 ====================
CHECKOUT_HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>退房提醒</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        :root{--s:#9CAF88;--sd:#7A9568;--n:#1A2A4A;--c:#FAF8F5;--g:#C9A961;--w:#fff}
        body{font-family:-apple-system,'Noto Sans SC',sans-serif;background:linear-gradient(135deg,#2a3f5f 0%,#1a2a4a 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;animation:fadeIn .5s ease}
        @keyframes fadeIn{from{opacity:0}to{opacity:1}}
        @keyframes slideUp{from{opacity:0;transform:translateY(30px) scale(.95)}to{opacity:1;transform:translateY(0) scale(1)}}
        @keyframes checkPop{0%{transform:scale(0)}50%{transform:scale(1.2)}100%{transform:scale(1)}}
        .modal{background:var(--w);border-radius:24px;padding:32px 28px;width:100%;max-width:400px;position:relative;animation:slideUp .4s cubic-bezier(.4,0,.2,1);box-shadow:0 20px 60px rgba(0,0,0,.3)}
        .close{position:absolute;top:16px;right:16px;width:36px;height:36px;background:#f5f5f5;border:none;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s}
        .close:hover{background:#e0e0e0;transform:rotate(90deg)}
        .close svg{width:18px;height:18px;stroke:#999;stroke-width:2;fill:none}
        .title{font-size:1.4rem;font-weight:700;color:var(--n);margin-bottom:6px}
        .subtitle{font-size:.9rem;color:#888;margin-bottom:24px}
        .section{margin-bottom:20px}
        .section-title{font-size:.85rem;color:#666;margin-bottom:12px;font-weight:600}
        .rooms{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
        .room-btn{padding:14px 8px;border:2px solid #e8e2d8;border-radius:12px;background:linear-gradient(135deg,var(--w) 0%,#f8f6f3 100%);font-size:1rem;font-weight:600;cursor:pointer;transition:all .3s;text-align:center;font-family:inherit}
        .room-btn:hover{border-color:var(--s);transform:translateY(-2px)}
        .room-btn.selected{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border-color:var(--s)}
        .time-section{margin-top:20px;padding-top:20px;border-top:1px solid #f0f0f0;display:none}
        .time-section.show{display:block}
        .time-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
        .time-btn{padding:12px 8px;border:2px solid #e8e2d8;border-radius:10px;background:var(--w);font-size:.9rem;cursor:pointer;transition:all .3s;text-align:center;font-family:inherit;font-weight:500}
        .time-btn:hover{border-color:var(--s)}
        .time-btn.selected{background:var(--s);color:#fff;border-color:var(--s)}
        .note-input{width:100%;padding:12px 16px;border:2px solid #e8e2d8;border-radius:10px;font-size:.9rem;font-family:inherit;margin-top:12px;resize:none}
        .note-input:focus{outline:none;border-color:var(--s)}
        .submit{width:100%;padding:16px;background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border:none;border-radius:12px;font-size:1rem;font-weight:600;cursor:pointer;transition:all .3s;font-family:inherit;margin-top:20px;opacity:.5}
        .submit.active{opacity:1}
        .submit.active:hover{transform:translateY(-2px)}
        .success{text-align:center;padding:20px 0;display:none}
        .success-icon{width:72px;height:72px;background:linear-gradient(135deg,var(--s),var(--sd));border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;animation:checkPop .4s ease}
        .success svg{width:36px;height:36px;stroke:#fff;stroke-width:2;fill:none}
        .success h3{font-size:1.2rem;color:var(--n);margin-bottom:6px}
        .success p{font-size:.85rem;color:#888}
        .form-content.hidden{display:none}
    </style>
</head>
<body>
<div class="modal">
    <button class="close" onclick="location.reload()"><svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    <div class="form-content" id="formContent">
        <div class="title">退房提醒</div>
        <div class="subtitle">请选择您的房间和退房时间</div>
        <div class="section"><div class="section-title">选择房号</div><div class="rooms" id="roomSel"></div></div>
        <div class="section time-section" id="timeSection">
            <div class="section-title">退房时间（8:00-12:00）</div>
            <div class="time-grid">
                <button class="time-btn" onclick="selectTime(this,'8:00-9:00')">8:00-9:00</button>
                <button class="time-btn" onclick="selectTime(this,'9:00-10:00')">9:00-10:00</button>
                <button class="time-btn" onclick="selectTime(this,'10:00-11:00')">10:00-11:00</button>
                <button class="time-btn" onclick="selectTime(this,'11:00-12:00')">11:00-12:00</button>
            </div>
            <textarea class="note-input" id="noteInput" placeholder="备注信息（选填）" rows="2"></textarea>
        </div>
        <button class="submit" id="submitBtn" onclick="submitForm()">提交退房提醒</button>
    </div>
    <div class="success" id="successMsg">
        <div class="success-icon"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div>
        <h3>提交成功！</h3>
        <p id="resultMsg">退房提醒已记录</p>
    </div>
</div>
<script>
const rooms=['101','201','202','203','204','205','301','302','303','304','305','306'];
let selectedRoom='',selectedTime='';
document.getElementById('roomSel').innerHTML=rooms.map(r=>`<button class="room-btn" onclick="selectRoom('${r}')">${r}</button>`).join('');
function selectRoom(r){selectedRoom=r;selectedTime='';document.querySelectorAll('.room-btn').forEach(b=>b.classList.remove('selected'));event.target.classList.add('selected');document.querySelectorAll('.time-btn').forEach(b=>b.classList.remove('selected'));document.getElementById('timeSection').classList.add('show');document.getElementById('submitBtn').classList.remove('active')}
function selectTime(el,t){selectedTime=t;document.querySelectorAll('.time-btn').forEach(b=>b.classList.remove('selected'));el.classList.add('selected');document.getElementById('submitBtn').classList.add('active')}
async function submitForm(){if(!selectedRoom||!selectedTime)return;const b=document.getElementById('submitBtn');b.textContent='提交中...';b.disabled=true;const note=document.getElementById('noteInput').value;try{await fetch('/api/checkout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({room:selectedRoom,time:selectedTime,note:note})});document.getElementById('formContent').classList.add('hidden');document.getElementById('successMsg').style.display='block';document.getElementById('resultMsg').textContent=`${selectedRoom}房 退房时间：${selectedTime} 已记录`}catch(e){alert('提交失败');b.textContent='提交退房提醒';b.disabled=false}}
</script>
</body></html>'''

# ==================== API路由 ====================
@app.route('/')
def index(): return '<script>location.href="/breakfast"</script>'

@app.route('/breakfast')
def breakfast_page(): return BREAKFAST_HTML

@app.route('/cleaning')
def cleaning_page(): return CLEANING_HTML

@app.route('/checkout')
def checkout_page(): return CHECKOUT_HTML

@app.route('/admin')
def admin_page(): return ADMIN_HTML

@app.route('/api/breakfast', methods=['GET'])
def get_breakfast():
    days = request.args.get('days', 7, type=int)
    orders = load_firebase_data('breakfast')
    if days > 0:
        cutoff = datetime.now().timestamp() - (days * 86400)
        orders = [o for o in orders if datetime.fromisoformat(o['timestamp']).timestamp() > cutoff]
    return jsonify(orders)

@app.route('/api/breakfast', methods=['POST'])
def add_breakfast():
    data = request.json
    orders = load_firebase_data('breakfast')
    now = datetime.now()
    order = {
        'room': data.get('room', ''),
        'soup': data.get('soup', ''),
        'onion': data.get('onion', ''),
        'herb': data.get('herb', ''),
        'timestamp': now.isoformat(),
        'time': now.strftime('%H:%M'),
        'date': now.strftime('%Y-%m-%d')
    }
    orders.append(order)
    save_firebase_data('breakfast', orders)
    return jsonify({'success': True})

@app.route('/api/breakfast/mark', methods=['POST'])
def mark_breakfast():
    data = request.json
    orders = load_firebase_data('breakfast')
    for o in orders:
        if o['timestamp'] == data.get('timestamp'):
            o['status'] = data.get('status', 'seen')
            break
    save_firebase_data('breakfast', orders)
    return jsonify({'success': True})

@app.route('/api/cleaning', methods=['GET'])
def get_cleaning():
    days = request.args.get('days', 7, type=int)
    records = load_firebase_data('cleaning')
    if days > 0:
        cutoff = datetime.now().timestamp() - (days * 86400)
        records = [r for r in records if datetime.fromisoformat(r['timestamp']).timestamp() > cutoff]
    return jsonify(records)

@app.route('/api/cleaning', methods=['POST'])
def add_cleaning():
    data = request.json
    records = load_firebase_data('cleaning')
    now = datetime.now()
    record = {
        'room': data.get('room', ''),
        'need': data.get('need', ''),
        'time': data.get('time', ''),
        'note': data.get('note', ''),
        'timestamp': now.isoformat(),
        'time_submitted': now.strftime('%H:%M'),
        'date': now.strftime('%Y-%m-%d')
    }
    records.append(record)
    save_firebase_data('cleaning', records)
    return jsonify({'success': True})

@app.route('/api/cleaning/mark', methods=['POST'])
def mark_cleaning():
    data = request.json
    records = load_firebase_data('cleaning')
    for r in records:
        if r['timestamp'] == data.get('timestamp'):
            r['status'] = data.get('status', 'seen')
            break
    save_firebase_data('cleaning', records)
    return jsonify({'success': True})

@app.route('/api/checkout', methods=['GET'])
def get_checkout():
    days = request.args.get('days', 7, type=int)
    records = load_firebase_data('checkout')
    if days > 0:
        cutoff = datetime.now().timestamp() - (days * 86400)
        records = [r for r in records if datetime.fromisoformat(r['timestamp']).timestamp() > cutoff]
    return jsonify(records)

@app.route('/api/checkout', methods=['POST'])
def add_checkout():
    data = request.json
    records = load_firebase_data('checkout')
    now = datetime.now()
    record = {
        'room': data.get('room', ''),
        'time': data.get('time', ''),
        'note': data.get('note', ''),
        'timestamp': now.isoformat(),
        'submit_time': now.strftime('%H:%M'),
        'date': now.strftime('%Y-%m-%d')
    }
    records.append(record)
    save_firebase_data('checkout', records)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
