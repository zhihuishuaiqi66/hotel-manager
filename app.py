"""
小陈家·环洱度假美宿 酒店管理系统
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

BREAKFAST_FILE = os.path.join(DATA_DIR, 'breakfast.json')
CLEANING_FILE = os.path.join(DATA_DIR, 'cleaning.json')

ROOMS = ['101', '201', '202', '203', '204', '205', '301', '302', '303', '304', '305', '306']

BREAKFAST_FILE = os.path.join(DATA_DIR, 'breakfast.json')
CLEANING_FILE = os.path.join(DATA_DIR, 'cleaning.json')
CHECKOUT_FILE = os.path.join(DATA_DIR, 'checkout.json')

def load_json(filepath, default=None):
    if default is None: default = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f: return json.load(f)
        except: return default
    return default

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)

# ==================== 早餐页面（弹窗卡片式） ====================
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
        .time-select{padding:8px 14px;border:2px solid #e8e2d8;border-radius:8px;background:var(--w);font-size:.85rem;cursor:pointer;transition:all .3s;font-family:inherit}
        .time-select:hover{border-color:var(--s)}
        .time-select.selected{background:var(--s);color:#fff;border-color:var(--s)}
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
    <button class="close" onclick="location.reload()">
        <svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
    
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
                <div style="margin-top:16px">
                    <div style="font-size:.85rem;color:#888;margin-bottom:8px">用餐时间（8:00-10:00）</div>
                    <div style="display:flex;gap:8px;flex-wrap:wrap">
                        <button class="time-select" onclick="selectMealTime(this,'8:00-8:30')">8:00-8:30</button>
                        <button class="time-select" onclick="selectMealTime(this,'8:30-9:00')">8:30-9:00</button>
                        <button class="time-select" onclick="selectMealTime(this,'9:00-9:30')">9:00-9:30</button>
                        <button class="time-select" onclick="selectMealTime(this,'9:30-10:00')">9:30-10:00</button>
                    </div>
                </div>
                </div>
            </div>
        </div>
        
        <div id="bowlArea"></div>
        
        <button class="submit" id="submitBtn" onclick="submitAll()" disabled>提交全部订单</button>
    </div>
    
    <div class="success" id="successMsg">
        <div class="success-icon">
            <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <h3>预订成功！</h3>
        <p id="resultMsg">您的早餐已记录</p>
        <button class="btn-outline" onclick="location.reload()">继续预订</button>
    </div>
</div>

<script>
const rooms = ['101','201','202','203','204','205','301','302','303','304','305','306'];
let selectedRoom = '';
let bowlCount = 0;
let bowlData = {};
let mealTime = '';

document.getElementById('roomSel').innerHTML = rooms.map((r,i) => 
    `<button class="room-btn" onclick="selectRoom('${r}')" style="animation-delay:${i*0.05}s">${r}</button>`
).join('');

function selectRoom(room) {
    selectedRoom = room;
    document.querySelectorAll('.room-btn').forEach(b => b.classList.remove('selected'));
    event.target.classList.add('selected');
    document.getElementById('qtySection').style.display = 'block';
    if (bowlCount === 0) changeQty(1);
}

function changeQty(delta) {
    bowlCount = Math.max(1, Math.min(10, bowlCount + delta));
    document.getElementById('qty').textContent = bowlCount;
    renderBowls();
}

function renderBowls() {
    const area = document.getElementById('bowlArea');
    if (bowlCount === 0) { area.innerHTML = ''; checkSubmit(); return; }
    
    let html = '';
    for (let i = 1; i <= bowlCount; i++) {
        const d = bowlData[i] || {};
        html += `
        <div class="bowl">
            <div class="bowl-header">
                <div class="bowl-num">${i}</div>
                <div class="bowl-title">第 ${i} 碗</div>
            </div>
            <div class="opt-group">
                <div class="opt-row">
                    <span class="opt-label">汤底</span>
                    <div class="opt-btns">
                        <button class="obtn ${d.soup==='清汤'?'sel':''}" onclick="setBowl(${i},'soup','清汤')">清汤</button>
                        <button class="obtn ${d.soup==='红油'?'sel':''}" onclick="setBowl(${i},'soup','红油')">红油</button>
                    </div>
                </div>
                <div class="opt-row">
                    <span class="opt-label">葱花</span>
                    <div class="opt-btns">
                        <button class="obtn ${d.onion==='要'?'sel':''}" onclick="setBowl(${i},'onion','要')">要</button>
                        <button class="obtn ${d.onion==='不要'?'sel':''}" onclick="setBowl(${i},'onion','不要')">不要</button>
                    </div>
                </div>
                <div class="opt-row">
                    <span class="opt-label">香菜</span>
                    <div class="opt-btns">
                        <button class="obtn ${d.herb==='要'?'sel':''}" onclick="setBowl(${i},'herb','要')">要</button>
                        <button class="obtn ${d.herb==='不要'?'sel':''}" onclick="setBowl(${i},'herb','不要')">不要</button>
                    </div>
                </div>
            </div>
        </div>`;
    }
    area.innerHTML = html;
    checkSubmit();
}

function setBowl(num, key, val) {
    if (!bowlData[num]) bowlData[num] = {};
    bowlData[num][key] = val;
    renderBowls();
}

function selectMealTime(el, time) {
    mealTime = time;
    document.querySelectorAll('.time-select').forEach(b => b.classList.remove('selected'));
    el.classList.add('selected');
    checkSubmit();
}

function checkSubmit() {
    let allFilled = selectedRoom && bowlCount > 0 && mealTime;
    for (let i = 1; i <= bowlCount; i++) {
        const d = bowlData[i] || {};
        if (!d.soup || !d.onion || !d.herb) { allFilled = false; break; }
    }
    const btn = document.getElementById('submitBtn');
    btn.disabled = !allFilled;
    if (allFilled) btn.classList.add('active');
    else btn.classList.remove('active');
}

async function submitAll() {
    const btn = document.getElementById('submitBtn');
    btn.disabled = true;
    btn.textContent = '提交中...';
    
    let count = 0;
    for (let i = 1; i <= bowlCount; i++) {
        const d = bowlData[i];
        try {
            await fetch('/api/breakfast', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({room: selectedRoom, ...d, mealtime: mealTime})
            });
            count++;
        } catch(e) {}
    }
    
    document.getElementById('formContent').classList.add('hidden');
    document.getElementById('successMsg').style.display = 'block';
    document.getElementById('resultMsg').textContent = `${selectedRoom}房 ${count}碗早餐 ${mealTime}用餐 已记录`;
}
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
        .time-label{font-size:.85rem;color:#666;margin-bottom:12px;font-weight:500;display:flex;align-items:center;gap:6px}
        .time-label svg{width:16px;height:16px;stroke:var(--s);stroke-width:2;fill:none}
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
    <button class="close" onclick="location.reload()">
        <svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
    
    <div class="form-content" id="formContent">
        <div class="title">客房清洁服务</div>
        <div class="subtitle">请选择今日客房服务状态</div>
        
        <div class="section">
            <div class="section-title">选择房号</div>
            <div class="rooms" id="roomSel"></div>
        </div>
        
        <div class="section" id="optSection" style="display:none">
            <div class="section-title">服务选择</div>
            <div class="options">
                <div class="opt-card" onclick="selectOpt(this, 'yes')">
                    <div class="opt-icon">🧹</div>
                    <div class="opt-text">
                        <h4>需要清洁</h4>
                        <p>请选择期望打扫时间</p>
                    </div>
                    <div class="opt-check">
                        <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
                    </div>
                </div>
                <div class="opt-card" onclick="selectOpt(this, 'no')">
                    <div class="opt-icon">🚫</div>
                    <div class="opt-text">
                        <h4>免打扰</h4>
                        <p>今日无需清洁客房</p>
                    </div>
                    <div class="opt-check">
                        <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="time-section" id="timeSection">
            <div class="time-label">
                <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                期望打扫时间（16点前）
            </div>
            <div class="time-grid" id="timeGrid">
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
        <div class="success-icon">
            <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <h3>提交成功！</h3>
        <p id="resultMsg">您的选择已记录</p>
    </div>
</div>

<script>
const rooms = ['101','201','202','203','204','205','301','302','303','304','305','306'];
let selectedRoom = '';
let selectedOpt = '';
let selectedTime = '';

document.getElementById('roomSel').innerHTML = rooms.map((r,i) => 
    `<button class="room-btn" onclick="selectRoom('${r}')" style="animation-delay:${i*0.05}s">${r}</button>`
).join('');

function selectRoom(room) {
    selectedRoom = room;
    selectedOpt = '';
    selectedTime = '';
    document.querySelectorAll('.room-btn').forEach(b => b.classList.remove('selected'));
    event.target.classList.add('selected');
    document.querySelectorAll('.opt-card').forEach(c => c.classList.remove('selected'));
    document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('selected'));
    document.getElementById('optSection').style.display = 'block';
    document.getElementById('timeSection').classList.remove('show');
    document.getElementById('submitBtn').classList.remove('active');
}

function selectOpt(el, value) {
    selectedOpt = value;
    selectedTime = '';
    document.querySelectorAll('.opt-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
    document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('selected'));
    
    const timeSection = document.getElementById('timeSection');
    if (value === 'yes') {
        timeSection.classList.add('show');
    } else {
        timeSection.classList.remove('show');
    }
    checkForm();
}

function selectTime(el, time) {
    selectedTime = time;
    document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('selected'));
    el.classList.add('selected');
    checkForm();
}

function checkForm() {
    const btn = document.getElementById('submitBtn');
    if (selectedRoom && selectedOpt && (selectedOpt === 'no' || selectedTime)) {
        btn.classList.add('active');
    } else {
        btn.classList.remove('active');
    }
}

async function submitForm() {
    if (!selectedRoom || !selectedOpt) return;
    if (selectedOpt === 'yes' && !selectedTime) return;
    
    const btn = document.getElementById('submitBtn');
    btn.textContent = '提交中...';
    btn.disabled = true;
    
    const note = document.getElementById('noteInput').value;
    
    try {
        await fetch('/api/cleaning', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({room: selectedRoom, need: selectedOpt, time: selectedTime, note: note})
        });
        document.getElementById('formContent').classList.add('hidden');
        document.getElementById('successMsg').style.display = 'block';
        document.getElementById('resultMsg').textContent = 
            `${selectedRoom}房 ${selectedOpt==='yes'?'打扫时间：'+selectedTime:'免打扰'} 已记录`;
    } catch(e) {
        alert('提交失败，请重试');
        btn.textContent = '提交选择';
        btn.disabled = false;
    }
}
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
        @keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
        @keyframes glow{0%,100%{box-shadow:0 0 5px var(--s)}50%{box-shadow:0 0 20px var(--s)}}
        @keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
        @keyframes countUp{from{opacity:0;transform:scale(0.5)}to{opacity:1;transform:scale(1)}}
        
        .hd{background:linear-gradient(135deg,var(--n) 0%,#0f1a2e 100%);color:#fff;padding:20px;position:sticky;top:0;z-index:100;box-shadow:0 4px 20px rgba(0,0,0,.2)}
        .hdc{max-width:900px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}
        .hd-left{display:flex;align-items:center;gap:12px}
        .hd h1{font-size:1.3rem;font-weight:700;letter-spacing:.5px}
        .st{font-size:.75rem;display:flex;align-items:center;gap:8px;background:rgba(255,255,255,.15);padding:8px 16px;border-radius:20px;backdrop-filter:blur(10px)}
        .dot{width:10px;height:10px;background:#48BB78;border-radius:50%;animation:pulse 2s infinite;position:relative}
        .dot::after{content:'';position:absolute;top:-3px;left:-3px;right:-3px;bottom:-3px;border:2px solid #48BB78;border-radius:50%;animation:pulse 2s infinite}
        .ct{max-width:900px;margin:0 auto;padding:24px 20px}
        
        .stats{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:24px}
        .stat-card{background:#fff;border-radius:16px;padding:24px;box-shadow:0 4px 20px rgba(0,0,0,.06);position:relative;overflow:hidden;animation:slideIn .5s ease}
        .stat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,var(--s),var(--sd));transform:scaleX(0);transform-origin:left;transition:transform .5s ease}
        .stat-card:hover::before{transform:scaleX(1)}
        .stat-card:hover{transform:translateY(-4px);box-shadow:0 8px 30px rgba(0,0,0,.1)}
        .stat-icon{width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.5rem;margin-bottom:12px}
        .stat-card:first-child .stat-icon{background:linear-gradient(135deg,#e8f5e9 0%,#c8e6c9 100%)}
        .stat-card:last-child .stat-icon{background:linear-gradient(135deg,#fff3e0 0%,#ffe0b2 100%)}
        .stat-value{font-size:2.5rem;font-weight:700;color:var(--n);animation:countUp .6s ease}
        .stat-label{font-size:.85rem;color:#888;margin-top:4px}
        
        .sec{margin-bottom:28px;animation:slideIn .5s ease}
        .sh{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
        .stl{font-size:1.1rem;color:var(--n);display:flex;align-items:center;gap:12px;font-weight:700}
        .stl::before{content:'';width:4px;height:20px;background:linear-gradient(135deg,var(--s),var(--sd));border-radius:2px}
        .bdg{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;padding:6px 16px;border-radius:20px;font-size:.8rem;font-weight:600;box-shadow:0 2px 10px rgba(156,175,136,.3)}
        
        .cd{background:#fff;border-radius:20px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.06)}
        .oi{padding:16px 20px;border-bottom:1px solid #f5f5f5;display:flex;justify-content:space-between;align-items:center;font-size:.9rem;transition:all .3s ease}
        .oi:last-child{border-bottom:none}
        .oi:hover{background:linear-gradient(90deg,rgba(156,175,136,.05) 0%,transparent 100%)}
        .ot{color:var(--g);font-weight:600}
        .od{color:#666;flex:1;margin:0 16px}
        .em{text-align:center;padding:60px 20px;color:#aaa;font-size:.9rem}
        .em svg{width:64px;height:64px;stroke:#ddd;stroke-width:1;fill:none;margin-bottom:16px;opacity:.5}
        
        .refresh-btn{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border:none;border-radius:20px;font-size:.8rem;cursor:pointer;transition:all .3s;font-family:inherit}
        .refresh-btn:hover{transform:scale(1.05);box-shadow:0 4px 15px rgba(156,175,136,.4)}
        .refresh-btn svg{width:14px;height:14px;stroke:currentColor;stroke-width:2;fill:none}
        
        .time-badge{background:linear-gradient(135deg,#e3f2fd 0%,#bbdefb 100%);color:#1976d2;padding:4px 10px;border-radius:12px;font-size:.75rem;font-weight:500}
        .clean-badge{background:linear-gradient(135deg,#e8f5e9 0%,#c8e6c9 100%);color:#388e3c;padding:4px 10px;border-radius:12px;font-size:.75rem;font-weight:500}
        .skip-badge{background:linear-gradient(135deg,#fce4ec 0%,#f8bbd9 100%);color:#c2185b;padding:4px 10px;border-radius:12px;font-size:.75rem;font-weight:500}
        .done-badge{background:linear-gradient(135deg,#e3f2fd 0%,#bbdefb 100%);color:#1565c0;padding:4px 10px;border-radius:12px;font-size:.75rem;font-weight:500}
        .action-btn{padding:6px 12px;border:none;border-radius:8px;font-size:.75rem;cursor:pointer;transition:all .2s;font-family:inherit;font-weight:500;margin-left:8px}
        .action-btn.done{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff}
        .action-btn.done:hover{transform:scale(1.05)}
        .action-btn.seen{background:linear-gradient(135deg,var(--g),#b89a4a);color:#fff}
        .action-btn.seen:hover{transform:scale(1.05)}
        .action-btn.mute{background:linear-gradient(135deg,#9e9e9e,#757575);color:#fff}
        .action-btn.mute:hover{transform:scale(1.05)}
        .sound-control{position:fixed;bottom:20px;right:20px;z-index:100}
        .login-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:linear-gradient(135deg,#2a3f5f 0%,#1a2a4a 100%);display:flex;align-items:center;justify-content:center;z-index:1000}
        .login-card{background:#fff;border-radius:24px;padding:40px;width:100%;max-width:360px;text-align:center;animation:slideUp .4s ease}
        @keyframes slideUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
        .login-icon{width:80px;height:80px;background:linear-gradient(135deg,var(--s),var(--sd));border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 24px;font-size:2rem}
        .login-title{font-size:1.4rem;font-weight:700;color:var(--n);margin-bottom:8px}
        .login-subtitle{font-size:.9rem;color:#888;margin-bottom:28px}
        .login-input{width:100%;padding:16px;border:2px solid #e8e2d8;border-radius:12px;font-size:1rem;font-family:inherit;text-align:center;letter-spacing:0.1em;transition:all .3s}
        .login-input:focus{outline:none;border-color:var(--s);box-shadow:0 0 0 3px rgba(156,175,136,.2)}
        .login-btn{width:100%;padding:16px;background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border:none;border-radius:12px;font-size:1rem;font-weight:600;cursor:pointer;transition:all .3s;font-family:inherit;margin-top:20px}
        .login-btn:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(156,175,136,.4)}
        .login-error{color:var(--r);font-size:.85rem;margin-top:12px;display:none}
        .admin-content{display:none}
        .admin-content.show{display:block}
    </style>
</head>
<body>
<!-- 登录弹窗 -->
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

<!-- 管理内容 -->
<div class="admin-content" id="adminContent">
<div class="hd">
    <div class="hdc">
        <div class="hd-left">
            <h1>后台管理</h1>
        </div>
        <div class="st">
            <div class="dot"></div>
            <span>实时更新</span>
            <button class="refresh-btn" onclick="refreshWithSound()">
                <svg viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
                刷新
            </button>
        </div>
    </div>
</div>

<div class="ct">
    <div class="stats">
        <div class="stat-card">
            <div class="stat-icon">🍜</div>
            <div class="stat-value" id="oc">0</div>
            <div class="stat-label">早餐订单</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🧹</div>
            <div class="stat-value" id="cc">0</div>
            <div class="stat-label">清洁请求</div>
        </div>
    </div>
    
    <div class="sec">
        <div class="sh">
            <div class="stl">早餐订单</div>
            <select id="breakfastFilter" onchange="loadO()" style="padding:8px 12px;border:1px solid #ddd;border-radius:8px;font-size:.85rem;font-family:inherit;cursor:pointer">
                <option value="1">今天</option>
                <option value="3">近3天</option>
                <option value="7" selected>近7天</option>
                <option value="30">近30天</option>
            </select>
        </div>
        <div class="cd" id="ol">
            <div class="em">
                <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                <p>暂无订单</p>
            </div>
        </div>
    </div>
    
    <div class="sec">
        <div class="sh">
            <div class="stl">清洁请求</div>
            <select id="cleaningFilter" onchange="loadC()" style="padding:8px 12px;border:1px solid #ddd;border-radius:8px;font-size:.85rem;font-family:inherit;cursor:pointer">
                <option value="1">今天</option>
                <option value="3">近3天</option>
                <option value="7" selected>近7天</option>
                <option value="30">近30天</option>
            </select>
        </div>
        <div class="cd" id="cl">
            <div class="em">
                <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                <p>暂无请求</p>
            </div>
        </div>
    </div>
    
    <div class="sec">
        <div class="sh">
            <div class="stl">退房提醒</div>
            <select id="checkoutFilter" onchange="loadCK()" style="padding:8px 12px;border:1px solid #ddd;border-radius:8px;font-size:.85rem;font-family:inherit;cursor:pointer">
                <option value="1">今天</option>
                <option value="3">近3天</option>
                <option value="7" selected>近7天</option>
                <option value="30">近30天</option>
            </select>
        </div>
        <div class="cd" id="ckl">
            <div class="em">
                <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                <p>暂无退房提醒</p>
            </div>
        </div>
    </div>
</div>

<!-- 停止响声按钮 -->
<div class="sound-control">
    <button class="action-btn mute" id="soundBtn" onclick="toggleSound()" style="width:48px;height:48px;border-radius:50%;font-size:1.2rem;display:flex;align-items:center;justify-content:center;">
        <svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" stroke-width="2" fill="none"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
    </button>
</div>

<script>
let soundEnabled = true;
async function refresh(){await Promise.all([loadO(),loadC(),loadCK()]);}
async function loadO(){
    const days=document.getElementById('breakfastFilter').value;
    const r=await fetch(`/api/breakfast?days=${days}`);const o=await r.json();
    document.getElementById('oc').textContent=o.length;
    if(!o.length){
        document.getElementById('ol').innerHTML='<div class="em"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><p>暂无订单</p></div>';
        return;
    }
    const s=[...o].sort((a,b)=>new Date(b.timestamp)-new Date(a.timestamp));
    document.getElementById('ol').innerHTML=s.map((x,i)=>`
        <div class="oi" style="animation:slideIn .3s ease ${i*0.05}s both">
            <span class="ot">${x.room}房</span>
            <span class="od">汤:${x.soup} 葱:${x.onion} 香:${x.herb} ${x.mealtime?'| 用餐:'+x.mealtime:''}</span>
            ${x.status==='done'?'<span class="done-badge">已做好</span>':''}
            <span class="time-badge">${x.date} ${x.time}</span>
            ${x.status!=='done'?`<button class="action-btn done" onclick="markDone('${x.timestamp}')">已做好</button>`:''}
            ${x.status!=='seen'?`<button class="action-btn seen" onclick="markSeen('${x.timestamp}')">看到了</button>`:''}
        </div>
    `).join('');
}
async function loadC(){
    const days=document.getElementById('cleaningFilter').value;
    const r=await fetch(`/api/cleaning?days=${days}`);const c=await r.json();
    document.getElementById('cc').textContent=c.length;
    if(!c.length){
        document.getElementById('cl').innerHTML='<div class="em"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><p>暂无请求</p></div>';
        return;
    }
    const s=[...c].sort((a,b)=>new Date(b.timestamp)-new Date(a.timestamp));
    document.getElementById('cl').innerHTML=s.map((x,i)=>`
        <div class="oi" style="animation:slideIn .3s ease ${i*0.05}s both">
            <span class="ot">${x.room}房</span>
            <span class="${x.need==='yes'?'clean-badge':'skip-badge'}">${x.need==='yes'?'需要打扫':'免打扰'}</span>
            ${x.status==='done'?'<span class="done-badge">已打扫</span>':''}
            <span class="time-badge">${x.date} ${x.time}</span>
            ${x.status!=='done'?`<button class="action-btn done" onclick="markCleanDone('${x.timestamp}')">已打扫</button>`:''}
            ${x.status!=='seen'?`<button class="action-btn seen" onclick="markCleanSeen('${x.timestamp}')">看到了</button>`:''}
        </div>
    `).join('');
}

async function markDone(ts) {
    await fetch('/api/breakfast/mark', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({timestamp:ts, status:'done'})});
    loadO();
}

async function markSeen(ts) {
    await fetch('/api/breakfast/mark', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({timestamp:ts, status:'seen'})});
    loadO();
}

async function markCleanDone(ts) {
    await fetch('/api/cleaning/mark', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({timestamp:ts, status:'done'})});
    loadC();
}

async function markCleanSeen(ts) {
    await fetch('/api/cleaning/mark', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({timestamp:ts, status:'seen'})});
    loadC();
}

async function loadCK(){
    const days=document.getElementById('checkoutFilter').value;
    const r=await fetch(`/api/checkout?days=${days}`);const c=await r.json();
    if(!c.length){
        document.getElementById('ckl').innerHTML='<div class="em"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><p>暂无退房提醒</p></div>';
        return;
    }
    const s=[...c].sort((a,b)=>new Date(b.timestamp)-new Date(a.timestamp));
    document.getElementById('ckl').innerHTML=s.map((x,i)=>`
        <div class="oi" style="animation:slideIn .3s ease ${i*0.05}s both">
            <span class="ot">${x.room}房</span>
            <span class="clean-badge">退房时间：${x.time}</span>
            ${x.note?`<span class="od">${x.note}</span>`:''}
            <span class="time-badge">${x.date} ${x.submit_time}</span>
        </div>
    `).join('');
}

function toggleSound() {
    soundEnabled = !soundEnabled;
    document.getElementById('soundBtn').innerHTML = soundEnabled ? 
        '<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>' : 
        '<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/><line x1="1" y1="1" x2="23" y2="23"/></svg>';
}

function playNotification() {
    if (!soundEnabled) return;
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        gainNode.gain.setValueAtTime(0.3, audioCtx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
        oscillator.start(audioCtx.currentTime);
        oscillator.stop(audioCtx.currentTime + 0.3);
    } catch(e) {}
}

let lastO = 0, lastC = 0, lastCK = 0;
async function refreshWithSound() {
    const prevO = lastO, prevC = lastC, prevCK = lastCK;
    await Promise.all([loadO(), loadC(), loadCK()]);
    lastO = parseInt(document.getElementById('oc').textContent) || 0;
    lastC = parseInt(document.getElementById('cc').textContent) || 0;
    lastCK = document.getElementById('ckl').querySelectorAll('.oi').length;
    if (lastO > prevO || lastC > prevC || lastCK > prevCK) {
        playNotification();
    }
}

function checkLogin() {
    const input = document.getElementById('loginInput').value;
    if (input === '232566cc') {
        document.getElementById('loginOverlay').style.display = 'none';
        document.getElementById('adminContent').classList.add('show');
        refreshWithSound();
        setInterval(refreshWithSound, 3000);
    } else {
        document.getElementById('loginError').style.display = 'block';
        document.getElementById('loginInput').value = '';
        document.getElementById('loginInput').focus();
    }
}
</script>
</body></html>'''

# ==================== API路由 ====================
@app.route('/')
def index(): return '<script>location.href="/breakfast"</script>'

@app.route('/breakfast')
def breakfast_page(): return BREAKFAST_HTML

@app.route('/cleaning')
def cleaning_page(): return CLEANING_HTML

@app.route('/admin')
def admin_page(): return ADMIN_HTML

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
        .section-title{font-size:.85rem;color:#666;margin-bottom:12px;font-weight:600;display:flex;align-items:center;gap:8px}
        .section-title::before{content:'';width:4px;height:14px;background:linear-gradient(135deg,var(--s),var(--sd));border-radius:2px}
        .rooms{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
        .room-btn{padding:14px 8px;border:2px solid #e8e2d8;border-radius:12px;background:linear-gradient(135deg,var(--w) 0%,#f8f6f3 100%);font-size:1rem;font-weight:600;cursor:pointer;transition:all .3s;text-align:center;font-family:inherit}
        .room-btn:hover{border-color:var(--s);transform:translateY(-2px);box-shadow:0 4px 12px rgba(156,175,136,.3)}
        .room-btn.selected{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border-color:var(--s)}
        .time-section{margin-top:20px;padding-top:20px;border-top:1px solid #f0f0f0;display:none}
        .time-section.show{display:block}
        .time-label{font-size:.85rem;color:#666;margin-bottom:12px;font-weight:500}
        .time-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
        .time-btn{padding:12px 8px;border:2px solid #e8e2d8;border-radius:10px;background:var(--w);font-size:.9rem;cursor:pointer;transition:all .3s;text-align:center;font-family:inherit;font-weight:500}
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
    <button class="close" onclick="location.reload()">
        <svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
    
    <div class="form-content" id="formContent">
        <div class="title">退房提醒</div>
        <div class="subtitle">请选择您的房间和退房时间</div>
        
        <div class="section">
            <div class="section-title">选择房号</div>
            <div class="rooms" id="roomSel"></div>
        </div>
        
        <div class="section time-section" id="timeSection">
            <div class="section-title">退房时间</div>
            <div class="time-grid" id="timeGrid">
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
        <div class="success-icon">
            <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <h3>提交成功！</h3>
        <p id="resultMsg">退房提醒已记录</p>
    </div>
</div>

<script>
const rooms = ['101','201','202','203','204','205','301','302','303','304','305','306'];
let selectedRoom = '';
let selectedTime = '';

document.getElementById('roomSel').innerHTML = rooms.map((r,i) => 
    `<button class="room-btn" onclick="selectRoom('${r}')" style="animation-delay:${i*0.05}s">${r}</button>`
).join('');

function selectRoom(room) {
    selectedRoom = room;
    selectedTime = '';
    document.querySelectorAll('.room-btn').forEach(b => b.classList.remove('selected'));
    event.target.classList.add('selected');
    document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('selected'));
    document.getElementById('timeSection').classList.add('show');
    document.getElementById('submitBtn').classList.remove('active');
}

function selectTime(el, time) {
    selectedTime = time;
    document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('selected'));
    el.classList.add('selected');
    document.getElementById('submitBtn').classList.add('active');
}

async function submitForm() {
    if (!selectedRoom || !selectedTime) return;
    
    const btn = document.getElementById('submitBtn');
    btn.textContent = '提交中...';
    btn.disabled = true;
    
    const note = document.getElementById('noteInput').value;
    
    try {
        await fetch('/api/checkout', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({room: selectedRoom, time: selectedTime, note: note})
        });
        document.getElementById('formContent').classList.add('hidden');
        document.getElementById('successMsg').style.display = 'block';
        document.getElementById('resultMsg').textContent = 
            `${selectedRoom}房 退房时间：${selectedTime} 已记录`;
    } catch(e) {
        alert('提交失败，请重试');
        btn.textContent = '提交退房提醒';
        btn.disabled = false;
    }
}
</script>
</body></html>'''

@app.route('/api/breakfast', methods=['GET'])
def get_breakfast():
    days = request.args.get('days', 7, type=int)
    orders = load_json(BREAKFAST_FILE, [])
    if days > 0:
        cutoff = datetime.now().timestamp() - (days * 86400)
        orders = [o for o in orders if datetime.fromisoformat(o['timestamp']).timestamp() > cutoff]
    return jsonify(orders)

@app.route('/api/breakfast', methods=['POST'])
def add_breakfast():
    data = request.json
    orders = load_json(BREAKFAST_FILE, [])
    now = datetime.now()
    order = {
        'room': data.get('room', ''),
        'soup': data.get('soup', ''),
        'onion': data.get('onion', ''),
        'herb': data.get('herb', ''),
        'mealtime': data.get('mealtime', ''),
        'timestamp': now.isoformat(),
        'time': now.strftime('%H:%M'),
        'date': now.strftime('%Y-%m-%d')
    }
    orders.append(order)
    save_json(BREAKFAST_FILE, orders)
    return jsonify({'success': True})

@app.route('/api/breakfast/mark', methods=['POST'])
def mark_breakfast():
    data = request.json
    orders = load_json(BREAKFAST_FILE, [])
    for o in orders:
        if o['timestamp'] == data.get('timestamp'):
            o['status'] = data.get('status', 'seen')
            break
    save_json(BREAKFAST_FILE, orders)
    return jsonify({'success': True})

@app.route('/api/cleaning', methods=['GET'])
def get_cleaning():
    days = request.args.get('days', 7, type=int)
    records = load_json(CLEANING_FILE, [])
    if days > 0:
        cutoff = datetime.now().timestamp() - (days * 86400)
        records = [r for r in records if datetime.fromisoformat(r['timestamp']).timestamp() > cutoff]
    return jsonify(records)

@app.route('/api/cleaning', methods=['POST'])
def add_cleaning():
    data = request.json
    records = load_json(CLEANING_FILE, [])
    now = datetime.now()
    record = {
        'room': data.get('room', ''),
        'need': data.get('need', ''),
        'timestamp': now.isoformat(),
        'time': now.strftime('%H:%M'),
        'date': now.strftime('%Y-%m-%d')
    }
    records.append(record)
    save_json(CLEANING_FILE, records)
    return jsonify({'success': True})

@app.route('/api/cleaning/mark', methods=['POST'])
def mark_cleaning():
    data = request.json
    records = load_json(CLEANING_FILE, [])
    for r in records:
        if r['timestamp'] == data.get('timestamp'):
            r['status'] = data.get('status', 'seen')
            break
    save_json(CLEANING_FILE, records)
    return jsonify({'success': True})

@app.route('/api/checkout', methods=['GET'])
def get_checkout():
    days = request.args.get('days', 7, type=int)
    records = load_json(CHECKOUT_FILE, [])
    if days > 0:
        cutoff = datetime.now().timestamp() - (days * 86400)
        records = [r for r in records if datetime.fromisoformat(r['timestamp']).timestamp() > cutoff]
    return jsonify(records)

@app.route('/api/checkout', methods=['POST'])
def add_checkout():
    data = request.json
    records = load_json(CHECKOUT_FILE, [])
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
    save_json(CHECKOUT_FILE, records)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
