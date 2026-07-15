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

# ==================== 早餐页面（展开式批量选择） ====================
BREAKFAST_HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>早餐预订</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        :root{--s:#9CAF88;--sd:#7A9568;--n:#1A2A4A;--c:#FAF8F5;--g:#C9A961;--r:#E53E3E}
        body{font-family:-apple-system,sans-serif;background:linear-gradient(180deg,var(--c),#f5f0e8);min-height:100vh;padding:16px}
        .ct{max-width:420px;margin:0 auto}
        .hd{text-align:center;padding:16px 0}
        .hd h1{font-size:1.3rem;color:var(--n);margin-bottom:4px}
        .hd p{font-size:.8rem;color:#7A7A7A}
        .card{background:#fff;border-radius:16px;padding:20px;margin-bottom:16px;box-shadow:0 2px 12px rgba(0,0,0,.06)}
        .label{font-size:.85rem;color:#666;margin-bottom:10px;font-weight:500}
        .rooms{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
        .rbtn{padding:12px 8px;border:2px solid #e8e2d8;border-radius:10px;background:var(--c);font-size:.95rem;font-weight:500;cursor:pointer;transition:all .2s;text-align:center;font-family:inherit}
        .rbtn:hover{border-color:var(--s)}
        .rbtn.sel{background:var(--s);color:#fff;border-color:var(--s)}
        .expand{max-height:0;overflow:hidden;transition:max-height .4s ease;margin-top:16px}
        .expand.open{max-height:2000px}
        .qty-row{display:flex;align-items:center;justify-content:center;gap:20px;padding:16px 0}
        .qbtn{width:44px;height:44px;border-radius:50%;border:2px solid #e8e2d8;background:var(--c);font-size:1.4rem;cursor:pointer;transition:all .2s;font-family:inherit;display:flex;align-items:center;justify-content:center}
        .qbtn:hover{border-color:var(--s)}
        .qnum{font-size:2rem;font-weight:700;color:var(--n);min-width:50px;text-align:center}
        .bowl{background:#f8f6f3;border-radius:12px;padding:16px;margin-bottom:12px;border-left:4px solid var(--g)}
        .bowl-title{font-size:.9rem;font-weight:600;color:var(--n);margin-bottom:12px;display:flex;align-items:center;gap:8px}
        .bowl-title span{background:var(--g);color:#fff;width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.75rem}
        .opts{display:flex;flex-direction:column;gap:10px}
        .opt-row{display:flex;align-items:center;gap:10px}
        .opt-label{font-size:.8rem;color:#888;width:40px;flex-shrink:0}
        .opt-btns{display:flex;gap:8px;flex:1}
        .obtn{flex:1;padding:10px;border:2px solid #e8e2d8;border-radius:8px;background:var(--c);font-size:.85rem;cursor:pointer;transition:all .2s;text-align:center;font-family:inherit}
        .obtn:hover{border-color:var(--s)}
        .obtn.sel{background:var(--s);color:#fff;border-color:var(--s)}
        .submit{width:100%;padding:16px;background:linear-gradient(135deg,var(--g),#9C7E3A);color:#fff;border:none;border-radius:12px;font-size:1rem;font-weight:600;cursor:pointer;transition:all .2s;font-family:inherit}
        .submit:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(201,169,97,.4)}
        .submit:disabled{opacity:.4;cursor:not-allowed;transform:none}
        .success{text-align:center;padding:30px 20px;display:none}
        .success svg{width:56px;height:56px;stroke:var(--s);stroke-width:1.5;fill:none;margin-bottom:12px}
        .success h3{font-size:1.1rem;color:var(--n);margin-bottom:6px}
        .success p{font-size:.85rem;color:#888}
        .success button{margin-top:16px;padding:12px 24px;background:var(--s);color:#fff;border:none;border-radius:8px;cursor:pointer;font-family:inherit}
        .ft{text-align:center;margin-top:16px;font-size:.7rem;color:#bbb}
    </style>
</head>
<body>
<div class="ct">
    <div class="hd"><h1>早餐预订</h1><p>小陈家·环洱度假美宿</p></div>
    
    <div id="mainForm">
        <div class="card">
            <div class="label">第一步：选择房号</div>
            <div class="rooms" id="roomSel"></div>
        </div>
        
        <div class="card" id="qtyCard" style="display:none">
            <div class="label">第二步：选择份数</div>
            <div class="qty-row">
                <button class="qbtn" onclick="changeQty(-1)">−</button>
                <span class="qnum" id="qty">1</span>
                <button class="qbtn" onclick="changeQty(1)">+</button>
            </div>
        </div>
        
        <div class="expand" id="bowlArea"></div>
        
        <div id="submitArea" style="display:none;padding:0 0 16px">
            <button class="submit" id="submitBtn" onclick="submitAll()">提交全部订单</button>
        </div>
    </div>
    
    <div class="success" id="successMsg">
        <svg viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        <h3>预订成功！</h3>
        <p id="resultMsg"></p>
        <button onclick="location.reload()">继续预订</button>
    </div>
    
    <div class="ft">步行5分钟直达洱海S湾</div>
</div>

<script>
const rooms = ['101','201','202','203','204','205','301','302','303','304','305','306'];
let selectedRoom = '';
let bowlCount = 0;
let bowlData = {};

// 渲染房号按钮
document.getElementById('roomSel').innerHTML = rooms.map(r => 
    `<button class="rbtn" onclick="selectRoom('${r}')">${r}</button>`
).join('');

function selectRoom(room) {
    selectedRoom = room;
    document.querySelectorAll('.rbtn').forEach(b => b.classList.remove('sel'));
    event.target.classList.add('sel');
    document.getElementById('qtyCard').style.display = 'block';
    if (bowlCount === 0) changeQty(1);
}

function changeQty(delta) {
    bowlCount = Math.max(1, Math.min(10, bowlCount + delta));
    document.getElementById('qty').textContent = bowlCount;
    renderBowls();
}

function renderBowls() {
    const area = document.getElementById('bowlArea');
    const submitArea = document.getElementById('submitArea');
    
    if (bowlCount === 0) {
        area.classList.remove('open');
        submitArea.style.display = 'none';
        return;
    }
    
    let html = '';
    for (let i = 1; i <= bowlCount; i++) {
        const d = bowlData[i] || {};
        html += `
        <div class="bowl">
            <div class="bowl-title"><span>${i}</span>第 ${i} 碗</div>
            <div class="opts">
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
    area.classList.add('open');
    submitArea.style.display = 'block';
    checkSubmit();
}

function setBowl(num, key, val) {
    if (!bowlData[num]) bowlData[num] = {};
    bowlData[num][key] = val;
    renderBowls();
}

function checkSubmit() {
    let allFilled = true;
    for (let i = 1; i <= bowlCount; i++) {
        const d = bowlData[i] || {};
        if (!d.soup || !d.onion || !d.herb) { allFilled = false; break; }
    }
    document.getElementById('submitBtn').disabled = !allFilled;
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
    
    document.getElementById('mainForm').style.display = 'none';
    document.getElementById('successMsg').style.display = 'block';
    document.getElementById('resultMsg').textContent = `${selectedRoom}房 ${count}碗早餐已记录`;
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
        :root{--s:#9CAF88;--sd:#7A9568;--n:#1A2A4A;--c:#FAF8F5;--r:#E53E3E;--g:#C9A961}
        body{font-family:-apple-system,sans-serif;background:linear-gradient(180deg,var(--c),#f5f0e8);min-height:100vh;padding:16px}
        .ct{max-width:420px;margin:0 auto}
        .hd{text-align:center;padding:16px 0}
        .hd h1{font-size:1.3rem;color:var(--n);margin-bottom:4px}
        .hd p{font-size:.8rem;color:#7A7A7A}
        .card{background:#fff;border-radius:16px;padding:24px;box-shadow:0 2px 12px rgba(0,0,0,.06)}
        .label{font-size:.85rem;color:#666;margin-bottom:12px;font-weight:500}
        .rooms{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:20px}
        .rbtn{padding:12px 8px;border:2px solid #e8e2d8;border-radius:10px;background:var(--c);font-size:1rem;font-weight:500;cursor:pointer;transition:all .2s;text-align:center;font-family:inherit}
        .rbtn:hover{border-color:var(--s)}
        .rbtn.sel{background:var(--s);color:#fff;border-color:var(--s)}
        .expand{max-height:0;overflow:hidden;transition:max-height .4s ease}
        .expand.open{max-height:500px}
        .opts{display:flex;gap:12px;padding-top:16px}
        .opt{flex:1;padding:18px 16px;border:2px solid #e8e2d8;border-radius:12px;background:var(--c);font-size:1rem;cursor:pointer;transition:all .2s;text-align:center;font-family:inherit;font-weight:500}
        .opt:hover{border-color:var(--s)}
        .opt.yes.sel{background:var(--s);color:#fff;border-color:var(--s)}
        .opt.no.sel{background:var(--r);color:#fff;border-color:var(--r)}
        .submit{width:100%;padding:16px;background:linear-gradient(135deg,var(--g),#9C7E3A);color:#fff;border:none;border-radius:12px;font-size:1rem;font-weight:600;cursor:pointer;transition:all .2s;font-family:inherit;margin-top:16px}
        .submit:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(201,169,97,.4)}
        .submit:disabled{opacity:.4;cursor:not-allowed;transform:none}
        .success{text-align:center;padding:40px 20px;display:none}
        .success svg{width:56px;height:56px;stroke:var(--s);stroke-width:1.5;fill:none;margin-bottom:12px}
        .success h3{font-size:1.1rem;color:var(--n);margin-bottom:6px}
        .success p{font-size:.85rem;color:#888}
        .success button{margin-top:16px;padding:12px 24px;background:var(--s);color:#fff;border:none;border-radius:8px;cursor:pointer;font-family:inherit}
        .ft{text-align:center;margin-top:16px;font-size:.7rem;color:#bbb}
    </style>
</head>
<body>
<div class="ct">
    <div class="hd"><h1>客房清洁</h1><p>小陈家·环洱度假美宿</p></div>
    
    <div id="mainForm" class="card">
        <div class="label">选择您的房号</div>
        <div class="rooms" id="roomSel"></div>
        
        <div class="expand" id="optArea">
            <div class="label">今日是否需要打扫？</div>
            <div class="opts">
                <button class="opt yes" onclick="selectOpt('yes')">需要打扫</button>
                <button class="opt no" onclick="selectOpt('no')">免打扰</button>
            </div>
            <button class="submit" id="submitBtn" onclick="submitForm()" disabled>提交</button>
        </div>
    </div>
    
    <div class="success" id="successMsg">
        <svg viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        <h3>提交成功！</h3>
        <p id="resultMsg"></p>
        <button onclick="location.reload()">返回</button>
    </div>
    
    <div class="ft">感谢您的配合</div>
</div>

<script>
const rooms = ['101','201','202','203','204','205','301','302','303','304','305','306'];
let selectedRoom = '';
let selectedOpt = '';

document.getElementById('roomSel').innerHTML = rooms.map(r => 
    `<button class="rbtn" onclick="selectRoom('${r}')">${r}</button>`
).join('');

function selectRoom(room) {
    selectedRoom = room;
    selectedOpt = '';
    document.querySelectorAll('.rbtn').forEach(b => b.classList.remove('sel'));
    event.target.classList.add('sel');
    document.querySelectorAll('.opt').forEach(b => b.classList.remove('sel'));
    document.getElementById('optArea').classList.add('open');
    document.getElementById('submitBtn').disabled = true;
}

function selectOpt(opt) {
    selectedOpt = opt;
    document.querySelectorAll('.opt').forEach(b => b.classList.remove('sel'));
    event.target.classList.add('sel');
    document.getElementById('submitBtn').disabled = false;
}

async function submitForm() {
    const btn = document.getElementById('submitBtn');
    btn.disabled = true;
    btn.textContent = '提交中...';
    
    try {
        await fetch('/api/cleaning', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({room: selectedRoom, need: selectedOpt})
        });
        document.getElementById('mainForm').style.display = 'none';
        document.getElementById('successMsg').style.display = 'block';
        document.getElementById('resultMsg').textContent = 
            `${selectedRoom}房 ${selectedOpt==='yes'?'需要打扫':'免打扰'} 已记录`;
    } catch(e) {
        alert('提交失败');
        btn.disabled = false;
        btn.textContent = '提交';
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
        body{font-family:-apple-system,sans-serif;background:var(--c);min-height:100vh}
        .hd{background:linear-gradient(135deg,var(--n),#0f1a2e);color:#fff;padding:16px 20px;position:sticky;top:0;z-index:100}
        .hdc{max-width:800px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}
        .hd h1{font-size:1.1rem}
        .st{font-size:.75rem;opacity:.7;display:flex;align-items:center;gap:6px}
        .dot{width:8px;height:8px;background:#48BB78;border-radius:50%;animation:p 2s infinite}
        @keyframes p{0%,100%{opacity:1}50%{opacity:.5}}
        .ct{max-width:800px;margin:0 auto;padding:16px}
        .sec{margin-bottom:20px}
        .sh{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
        .stl{font-size:.95rem;color:var(--n);display:flex;align-items:center;gap:8px}
        .stl::before{content:'';width:4px;height:14px;background:var(--s);border-radius:2px}
        .bdg{background:var(--s);color:#fff;padding:3px 10px;border-radius:12px;font-size:.75rem;font-weight:500}
        .cd{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.05)}
        .oi{padding:12px 16px;border-bottom:1px solid #f0f0f0;display:flex;justify-content:space-between;align-items:center;font-size:.85rem}
        .oi:last-child{border-bottom:none}
        .ot{color:var(--g);font-weight:500}
        .od{color:#666}
        .em{text-align:center;padding:30px;color:#aaa;font-size:.85rem}
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

# ==================== API路由 ====================
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
    save_json(BREAKFAST_FILE, orders)
    return jsonify({'success': True})

@app.route('/api/cleaning', methods=['GET'])
def get_cleaning(): return jsonify(load_json(CLEANING_FILE, []))

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
