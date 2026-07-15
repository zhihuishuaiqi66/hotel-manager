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
def load_json(filepath, default=None):
    if default is None: default = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f: return json.load(f)
        except: return default
    return default
def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)
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
function checkSubmit() {
    let allFilled = selectedRoom && bowlCount > 0;
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
                body: JSON.stringify({room: selectedRoom, ...d})
            });
            count++;
        } catch(e) {}
    }
    document.getElementById('formContent').classList.add('hidden');
    document.getElementById('successMsg').style.display = 'block';
    document.getElementById('resultMsg').textContent = `${selectedRoom}房 ${count}碗早餐已记录`;
}
</script>
</body></html>'''
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
        @keyframes checkPop{0%{transform:scale(0)}50%{transform:scale(1.2)}100%{transform:scale(1)}}
        .modal{background:var(--w);border-radius:24px;padding:32px 28px;width:100%;max-width:400px;position:relative;animation:slideUp .4s cubic-bezier(.4,0,.2,1);box-shadow:0 20px 60px rgba(0,0,0,.3)}
        .close{position:absolute;top:16px;right:16px;width:36px;height:36px;background:#f5f5f5;border:none;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s}
        .close:hover{background:#e0e0e0;transform:rotate(90deg)}
        .close svg{width:18px;height:18px;stroke:#999;stroke-width:2;fill:none}
        .title{font-size:1.4rem;font-weight:700;color:var(--n);margin-bottom:8px}
        .subtitle{font-size:.9rem;color:#888;margin-bottom:28px}
        .field-label{font-size:.85rem;color:#666;margin-bottom:10px;font-weight:500}
        .room-input{width:100%;padding:16px;border:2px solid #e8e2d8;border-radius:12px;font-size:1rem;font-family:inherit;transition:all .2s;appearance:none;cursor:pointer;background:var(--w) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%23999' stroke-width='2' fill='none'/%3E%3C/svg%3E") no-repeat right 16px center}
        .room-input:focus{outline:none;border-color:var(--s);box-shadow:0 0 0 3px rgba(156,175,136,.2)}
        .room-input option{padding:12px;font-size:1rem}
        .options{display:flex;flex-direction:column;gap:12px;margin-top:24px}
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
        .submit{width:100%;padding:16px;background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border:none;border-radius:12px;font-size:1rem;font-weight:600;cursor:pointer;transition:all .3s;font-family:inherit;margin-top:24px;opacity:.5}
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
        <div class="field-label">房间号</div>
        <select class="room-input" id="roomSelect" onchange="checkForm()">
            <option value="" disabled selected>请选择您的房间号</option>
        </select>
        <div class="options">
            <div class="opt-card" onclick="selectOpt(this, 'yes')">
                <div class="opt-icon">🧹</div>
                <div class="opt-text">
                    <h4>需要清洁</h4>
                    <p>请在上午10点前选择</p>
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
const select = document.getElementById('roomSelect');
rooms.forEach(r => {
    const opt = document.createElement('option');
    opt.value = r;
    opt.textContent = r + '房';
    select.appendChild(opt);
});
function selectOpt(el, value) {
    selectedOpt = value;
    document.querySelectorAll('.opt-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
    checkForm();
}
function checkForm() {
    selectedRoom = document.getElementById('roomSelect').value;
    const btn = document.getElementById('submitBtn');
    if (selectedRoom && selectedOpt) {
        btn.classList.add('active');
    } else {
        btn.classList.remove('active');
    }
}
async function submitForm() {
    if (!selectedRoom || !selectedOpt) return;
    const btn = document.getElementById('submitBtn');
    btn.textContent = '提交中...';
    btn.disabled = true;
    try {
        await fetch('/api/cleaning', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({room: selectedRoom, need: selectedOpt})
        });
        document.getElementById('formContent').classList.add('hidden');
        document.getElementById('successMsg').style.display = 'block';
        document.getElementById('resultMsg').textContent = 
            `${selectedRoom}房 ${selectedOpt==='yes'?'需要清洁':'免打扰'} 已记录`;
    } catch(e) {
        alert('提交失败，请重试');
        btn.textContent = '提交选择';
        btn.disabled = false;
    }
}
</script>
</body></html>'''
ADMIN_HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>后台管理</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        :root{--s:#9CAF88;--sd:#7A9568;--n:#1A2A4A;--c:#FAF8F5;--g:#C9A961;--r:#E53E3E}
        body{font-family:-apple-system,'Noto Sans SC',sans-serif;background:var(--c);min-height:100vh}
        .hd{background:linear-gradient(135deg,var(--n),#0f1a2e);color:#fff;padding:16px 20px;position:sticky;top:0;z-index:100}
        .hdc{max-width:800px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}
        .hd h1{font-size:1.2rem;font-weight:600}
        .st{font-size:.75rem;opacity:.8;display:flex;align-items:center;gap:8px;background:rgba(255,255,255,.1);padding:6px 12px;border-radius:20px}
        .dot{width:8px;height:8px;background:#48BB78;border-radius:50%;animation:pulse 2s infinite}
        @keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(72,187,120,.4)}50%{opacity:.8;box-shadow:0 0 0 6px rgba(72,187,120,0)}}
        .ct{max-width:800px;margin:0 auto;padding:20px}
        .sec{margin-bottom:24px}
        .sh{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
        .stl{font-size:1rem;color:var(--n);display:flex;align-items:center;gap:10px;font-weight:600}
        .stl::before{content:'';width:4px;height:18px;background:linear-gradient(135deg,var(--s),var(--sd));border-radius:2px}
        .bdg{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;padding:4px 12px;border-radius:20px;font-size:.75rem;font-weight:600}
        .cd{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,.06)}
        .oi{padding:14px 18px;border-bottom:1px solid #f0f0f0;display:flex;justify-content:space-between;align-items:center;font-size:.9rem}
        .oi:last-child{border-bottom:none}
        .ot{color:var(--g);font-weight:600}
        .od{color:#666}
        .em{text-align:center;padding:40px;color:#aaa;font-size:.9rem}
    </style>
</head>
<body>
<div class="hd"><div class="hdc"><h1>后台管理</h1><div class="st"><div class="dot"></div><span>实时更新</span></div></div></div>
<div class="ct">
    <div class="sec">
        <div class="sh"><div class="stl">早餐订单</div><div class="bdg" id="oc">0</div></div>
        <div class="cd" id="ol"><div class="em">暂无订单</div></div>
    </div>
    <div class="sec">
        <div class="sh"><div class="stl">清洁请求</div><div class="bdg" id="cc">0</div></div>
        <div class="cd" id="cl"><div class="em">暂无请求</div></div>
    </div>
</div>
<script>
async function refresh(){await Promise.all([loadO(),loadC()]);}
async function loadO(){
    const r=await fetch('/api/breakfast');const o=await r.json();
    document.getElementById('oc').textContent=o.length;
    if(!o.length){document.getElementById('ol').innerHTML='<div class="em">暂无订单</div>';return;}
    const s=[...o].sort((a,b)=>new Date(b.timestamp)-new Date(a.timestamp)).slice(0,30);
    document.getElementById('ol').innerHTML=s.map(x=>`<div class="oi"><span class="ot">${x.room}房</span><span class="od">汤:${x.soup} 葱:${x.onion} 香:${x.herb}</span><span class="ot">${x.time}</span></div>`).join('');
}
async function loadC(){
    const r=await fetch('/api/cleaning');const c=await r.json();
    document.getElementById('cc').textContent=c.length;
    if(!c.length){document.getElementById('cl').innerHTML='<div class="em">暂无请求</div>';return;}
    const s=[...c].sort((a,b)=>new Date(b.timestamp)-new Date(a.timestamp)).slice(0,20);
    document.getElementById('cl').innerHTML=s.map(x=>`<div class="oi"><span class="ot">${x.room}房</span><span class="${x.need==='yes'?'od':'ot'}">${x.need==='yes'?'需要打扫':'免打扰'}</span><span class="ot">${x.time}</span></div>`).join('');
}
refresh();setInterval(refresh,3000);
</script>
</body></html>'''
@app.route('/')
def index(): return '<script>location.href="/breakfast"</script>'
@app.route('/breakfast')
def breakfast_page(): return BREAKFAST_HTML
@app.route('/cleaning')
def cleaning_page(): return CLEANING_HTML
@app.route('/admin')
def admin_page(): return ADMIN_HTML
@app.route('/api/breakfast', methods=['GET'])
def get_breakfast(): return jsonify(load_json(BREAKFAST_FILE, []))
@app.route('/api/breakfast', methods=['POST'])
def add_breakfast():
    data = request.json
    orders = load_json(BREAKFAST_FILE, [])
    now = datetime.now()
    order = {'room': data.get('room', ''), 'soup': data.get('soup', ''), 'onion': data.get('onion', ''), 'herb': data.get('herb', ''), 'timestamp': now.isoformat(), 'time': now.strftime('%H:%M'), 'date': now.strftime('%Y-%m-%d')}
    orders.append(order)
    save_json(BREAKFAST_FILE, orders)
    return jsonify({'success': True})
@app.route('/api/cleaning', methods=['GET'])
def get_cleaning(): return jsonify(load_json(CLEANING_FILE, []))
@app.route('/api/cleaning', methods=['POST'])
def add_cleaning():
    data = request.json
    records = load_json(CLEANING_FILE, [])
    now = datetime.now()
    record = {'room': data.get('room', ''), 'need': data.get('need', ''), 'timestamp': now.isoformat(), 'time': now.strftime('%H:%M'), 'date': now.strftime('%Y-%m-%d')}
    records.append(record)
    save_json(CLEANING_FILE, records)
    return jsonify({'success': True})
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
