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
# 数据目录
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
BREAKFAST_FILE = os.path.join(DATA_DIR, 'breakfast.json')
CLEANING_FILE = os.path.join(DATA_DIR, 'cleaning.json')
# 房间列表
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
        :root{--s:#9CAF88;--sd:#7A9568;--n:#1A2A4A;--c:#FAF8F5;--g:#C9A961}
        body{font-family:-apple-system,sans-serif;background:linear-gradient(180deg,var(--c),#f5f0e8);min-height:100vh;padding:20px}
        .ct{max-width:400px;margin:0 auto}
        .hd{text-align:center;padding:20px 0}
        .hd h1{font-size:1.4rem;color:var(--n);margin-bottom:6px}
        .hd p{font-size:.85rem;color:#7A7A7A}
        .fc{background:#fff;border-radius:20px;padding:24px;box-shadow:0 4px 20px rgba(26,42,74,.08)}
        .og{margin-bottom:20px}
        .ol{font-size:.85rem;color:#333;margin-bottom:10px;font-weight:500}
        .ob{display:flex;gap:10px}
        .ob button{flex:1;padding:12px;border:2px solid #e8e2d8;border-radius:10px;background:var(--c);font-size:.9rem;cursor:pointer;transition:all .2s;font-family:inherit}
        .ob button:hover{border-color:var(--s)}
        .ob button.sel{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border-color:var(--s)}
        .room-sel{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:20px}
        .room-btn{padding:10px;border:2px solid #e8e2d8;border-radius:8px;background:var(--c);font-size:.9rem;cursor:pointer;transition:all .2s;text-align:center;font-family:inherit}
        .room-btn:hover{border-color:var(--s)}
        .room-btn.sel{background:var(--s);color:#fff;border-color:var(--s)}
        .qty-row{display:flex;align-items:center;justify-content:center;gap:16px;margin:20px 0}
        .qty-btn{width:40px;height:40px;border-radius:50%;border:2px solid #e8e2d8;background:var(--c);font-size:1.2rem;cursor:pointer;transition:all .2s;font-family:inherit}
        .qty-btn:hover{border-color:var(--s)}
        .qty-num{font-size:1.5rem;font-weight:600;color:var(--n);min-width:40px;text-align:center}
        .sb{width:100%;padding:14px;background:linear-gradient(135deg,var(--g),#9C7E3A);color:#fff;border:none;border-radius:12px;font-size:1rem;font-weight:500;cursor:pointer;margin-top:16px;transition:all .2s;font-family:inherit}
        .sb:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(201,169,97,.4)}
        .sb:disabled{opacity:.5;cursor:not-allowed;transform:none}
        .sm{display:none;text-align:center;padding:40px 20px}
        .sm svg{width:64px;height:64px;stroke:var(--s);stroke-width:1.5;fill:none;margin-bottom:16px}
        .sm h3{font-size:1.2rem;color:var(--n);margin-bottom:8px}
        .sm p{font-size:.9rem;color:#7A7A7A}
        .ft{text-align:center;margin-top:20px;font-size:.75rem;color:#aaa}
    </style>
</head>
<body>
<div class="ct">
    <div class="hd"><h1>早餐预订</h1><p>小陈家·环洱度假美宿</p></div>
    <div class="fc" id="form">
        <div class="og"><div class="ol">选择房号</div><div class="room-sel" id="roomSel"></div></div>
        <div class="og"><div class="ol">汤底选择</div><div class="ob"><button data-g="soup" data-v="清汤" onclick="sel(this)">清汤</button><button data-g="soup" data-v="红油" onclick="sel(this)">红油</button></div></div>
        <div class="og"><div class="ol">葱花</div><div class="ob"><button data-g="onion" data-v="要" onclick="sel(this)">要</button><button data-g="onion" data-v="不要" onclick="sel(this)">不要</button></div></div>
        <div class="og"><div class="ol">香菜</div><div class="ob"><button data-g="herb" data-v="要" onclick="sel(this)">要</button><button data-g="herb" data-v="不要" onclick="sel(this)">不要</button></div></div>
        <div class="og"><div class="ol">份数</div><div class="qty-row"><button class="qty-btn" onclick="changeQty(-1)">-</button><span class="qty-num" id="qty">1</span><button class="qty-btn" onclick="changeQty(1)">+</button></div></div>
        <button class="sb" id="btn" onclick="sub()" disabled>提交订单</button>
    </div>
    <div class="sm" id="ok">
        <svg viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        <h3>预订成功！</h3><p id="okMsg">您的早餐已记录</p>
        <button class="sb" onclick="reset()" style="margin-top:20px;background:var(--s)">继续预订</button>
    </div>
    <div class="ft">步行5分钟直达洱海S湾</div>
</div>
<script>
const rooms=['101','201','202','203','204','205','301','302','303','304','305','306'];
const s={room:'',qty:1};
document.getElementById('roomSel').innerHTML=rooms.map(r=>`<button class="room-btn" onclick="selRoom(this,'${r}')">${r}</button>`).join('');
function selRoom(b,r){document.querySelectorAll('.room-btn').forEach(x=>x.classList.remove('sel'));b.classList.add('sel');s.room=r;check();}
function sel(b){document.querySelectorAll(`[data-g="${b.dataset.g}"]`).forEach(x=>x.classList.remove('sel'));b.classList.add('sel');s[b.dataset.g]=b.dataset.v;check();}
function check(){document.getElementById('btn').disabled=!(s.room&&s.soup&&s.onion&&s.herb);}
function changeQty(d){s.qty=Math.max(1,Math.min(10,s.qty+d));document.getElementById('qty').textContent=s.qty;}
async function sub(){
    const b=document.getElementById('btn');b.disabled=true;b.textContent='提交中...';
    const data={...s,qty:s.qty};
    try{const r=await fetch('/api/breakfast',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
    if(r.ok){document.getElementById('form').style.display='none';document.getElementById('ok').style.display='block';document.getElementById('okMsg').textContent=`${s.room}房 ${s.qty}份早餐已记录`;}
    }catch(e){alert('提交失败');b.disabled=false;b.textContent='提交订单';}
}
function reset(){location.reload();}
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
        :root{--s:#9CAF88;--sd:#7A9568;--n:#1A2A4A;--c:#FAF8F5;--r:#E53E3E;--g:#C9A961}
        body{font-family:-apple-system,sans-serif;background:linear-gradient(180deg,var(--c),#f5f0e8);min-height:100vh;padding:20px}
        .ct{max-width:400px;margin:0 auto}
        .hd{text-align:center;padding:20px 0}
        .hd h1{font-size:1.4rem;color:var(--n);margin-bottom:6px}
        .hd p{font-size:.85rem;color:#7A7A7A}
        .fc{background:#fff;border-radius:20px;padding:24px;box-shadow:0 4px 20px rgba(26,42,74,.08)}
        .og{margin-bottom:20px}
        .ol{font-size:.85rem;color:#333;margin-bottom:10px;font-weight:500}
        .room-sel{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
        .room-btn{padding:12px;border:2px solid #e8e2d8;border-radius:8px;background:var(--c);font-size:1rem;cursor:pointer;transition:all .2s;text-align:center;font-family:inherit;font-weight:500}
        .room-btn:hover{border-color:var(--s)}
        .room-btn.sel{background:var(--s);color:#fff;border-color:var(--s)}
        .opt-sel{display:flex;gap:10px}
        .opt-btn{flex:1;padding:14px;border:2px solid #e8e2d8;border-radius:10px;background:var(--c);font-size:.95rem;cursor:pointer;transition:all .2s;text-align:center;font-family:inherit}
        .opt-btn:hover{border-color:var(--s)}
        .opt-btn.yes.sel{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border-color:var(--s)}
        .opt-btn.no.sel{background:linear-gradient(135deg,#E53E3E,#C53030);color:#fff;border-color:#E53E3E}
        .sb{width:100%;padding:14px;background:linear-gradient(135deg,var(--g),#9C7E3A);color:#fff;border:none;border-radius:12px;font-size:1rem;font-weight:500;cursor:pointer;margin-top:20px;transition:all .2s;font-family:inherit}
        .sb:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(201,169,97,.4)}
        .sb:disabled{opacity:.5;cursor:not-allowed;transform:none}
        .sm{display:none;text-align:center;padding:40px 20px}
        .sm svg{width:64px;height:64px;stroke:var(--s);stroke-width:1.5;fill:none;margin-bottom:16px}
        .sm h3{font-size:1.2rem;color:var(--n);margin-bottom:8px}
        .sm p{font-size:.9rem;color:#7A7A7A}
        .ft{text-align:center;margin-top:20px;font-size:.75rem;color:#aaa}
    </style>
</head>
<body>
<div class="ct">
    <div class="hd"><h1>客房清洁</h1><p>小陈家·环洱度假美宿</p></div>
    <div class="fc" id="form">
        <div class="og"><div class="ol">选择您的房号</div><div class="room-sel" id="roomSel"></div></div>
        <div class="og"><div class="ol">今日是否需要打扫？</div><div class="opt-sel"><button class="opt-btn yes" onclick="selOpt(this,'yes')">需要打扫</button><button class="opt-btn no" onclick="selOpt(this,'no')">免打扰</button></div></div>
        <button class="sb" id="btn" onclick="sub()" disabled>提交</button>
    </div>
    <div class="sm" id="ok">
        <svg viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        <h3>提交成功！</h3><p id="okMsg">已记录</p>
        <button class="sb" onclick="reset()" style="margin-top:20px;background:var(--s)">返回</button>
    </div>
    <div class="ft">感谢您的配合</div>
</div>
<script>
const rooms=['101','201','202','203','204','205','301','302','303','304','305','306'];
const s={room:'',need:''};
document.getElementById('roomSel').innerHTML=rooms.map(r=>`<button class="room-btn" onclick="selRoom(this,'${r}')">${r}</button>`).join('');
function selRoom(b,r){document.querySelectorAll('.room-btn').forEach(x=>x.classList.remove('sel'));b.classList.add('sel');s.room=r;check();}
function selOpt(b,v){document.querySelectorAll('.opt-btn').forEach(x=>x.classList.remove('sel'));b.classList.add('sel');s.need=v;check();}
function check(){document.getElementById('btn').disabled=!(s.room&&s.need);}
async function sub(){
    const b=document.getElementById('btn');b.disabled=true;b.textContent='提交中...';
    try{const r=await fetch('/api/cleaning',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(s)});
    if(r.ok){document.getElementById('form').style.display='none';document.getElementById('ok').style.display='block';
    document.getElementById('okMsg').textContent=`${s.room}房 ${s.need==='yes'?'需要打扫':'免打扰'}已记录`;}
    }catch(e){alert('提交失败');b.disabled=false;b.textContent='提交';}
}
function reset(){location.reload();}
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
        .bdg{background:var(--s);color:#fff;padding:3px 8px;border-radius:12px;font-size:.7rem}
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
    const s=[...o].sort((a,b)=>new Date(b.timestamp)-new Date(a.timestamp)).slice(0,20);
    document.getElementById('ol').innerHTML=s.map(x=>`<div class="oi"><span class="ot">${x.room}房 ${x.qty}份</span><span class="od">汤:${x.soup} 葱:${x.onion} 香:${x.herb}</span><span class="ot">${x.time}</span></div>`).join('');
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
    order = {
        'room': data.get('room', ''),
        'soup': data.get('soup', ''),
        'onion': data.get('onion', ''),
        'herb': data.get('herb', ''),
        'qty': data.get('qty', 1),
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
