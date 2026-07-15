"""
小陈家·环洱度假美宿 酒店管理系统
适配PythonAnywhere免费平台部署
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# PythonAnywhere数据目录（重启后不丢失）
DATA_DIR = '/home/你的用户名/data'  # 部署时改为你的用户名
# 本地测试用当前目录
if not os.path.exists(DATA_DIR):
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

os.makedirs(DATA_DIR, exist_ok=True)

BREAKFAST_FILE = os.path.join(DATA_DIR, 'breakfast.json')
ROOMS_FILE = os.path.join(DATA_DIR, 'rooms.json')

# 固定房间列表
DEFAULT_ROOMS = ['101', '201', '202', '203', '204', '205',
                 '301', '302', '303', '304', '305', '306']

def load_json(filepath, default=None):
    if default is None:
        default = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def init_rooms():
    if not os.path.exists(ROOMS_FILE):
        rooms = {room: '待打扫' for room in DEFAULT_ROOMS}
        save_json(ROOMS_FILE, rooms)

init_rooms()

# ==================== HTML模板 ====================

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
        .hd{text-align:center;padding:30px 0}
        .hd h1{font-size:1.5rem;color:var(--n);margin-bottom:8px}
        .hd p{font-size:.9rem;color:#7A7A7A}
        .fc{background:#fff;border-radius:20px;padding:28px;box-shadow:0 4px 20px rgba(26,42,74,.08)}
        .og{margin-bottom:24px}
        .ol{font-size:.85rem;color:#333;margin-bottom:12px;font-weight:500}
        .ob{display:flex;gap:12px}
        .ob button{flex:1;padding:14px;border:2px solid #e8e2d8;border-radius:12px;background:var(--c);font-size:.95rem;cursor:pointer;transition:all .2s;font-family:inherit}
        .ob button:hover{border-color:var(--s)}
        .ob button.sel{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border-color:var(--s)}
        .sb{width:100%;padding:16px;background:linear-gradient(135deg,var(--g),#9C7E3A);color:#fff;border:none;border-radius:12px;font-size:1rem;font-weight:500;cursor:pointer;margin-top:28px;transition:all .2s;font-family:inherit}
        .sb:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(201,169,97,.4)}
        .sb:disabled{opacity:.5;cursor:not-allowed;transform:none}
        .sm{display:none;text-align:center;padding:40px 20px}
        .sm svg{width:64px;height:64px;stroke:var(--s);stroke-width:1.5;fill:none;margin-bottom:16px}
        .sm h3{font-size:1.2rem;color:var(--n);margin-bottom:8px}
        .sm p{font-size:.9rem;color:#7A7A7A}
        .ft{text-align:center;margin-top:24px;font-size:.8rem;color:#aaa}
    </style>
</head>
<body>
<div class="ct">
    <div class="hd"><h1>早餐预订</h1><p>小陈家·环洱度假美宿</p></div>
    <div class="fc" id="form">
        <div class="og"><div class="ol">汤底选择</div><div class="ob"><button data-g="soup" data-v="清汤" onclick="sel(this)">清汤</button><button data-g="soup" data-v="红油" onclick="sel(this)">红油</button></div></div>
        <div class="og"><div class="ol">葱花</div><div class="ob"><button data-g="onion" data-v="要" onclick="sel(this)">要</button><button data-g="onion" data-v="不要" onclick="sel(this)">不要</button></div></div>
        <div class="og"><div class="ol">香菜</div><div class="ob"><button data-g="herb" data-v="要" onclick="sel(this)">要</button><button data-g="herb" data-v="不要" onclick="sel(this)">不要</button></div></div>
        <button class="sb" id="btn" onclick="sub()" disabled>提交订单</button>
    </div>
    <div class="sm" id="ok">
        <svg viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        <h3>预订成功！</h3><p>您的早餐已记录</p>
    </div>
    <div class="ft">步行5分钟直达洱海S湾</div>
</div>
<script>
const s={};
function sel(b){
    document.querySelectorAll(`[data-g="${b.dataset.g}"]`).forEach(x=>x.classList.remove('sel'));
    b.classList.add('sel');
    s[b.dataset.g]=b.dataset.v;
    document.getElementById('btn').disabled=!(s.soup&&s.onion&&s.herb);
}
async function sub(){
    const b=document.getElementById('btn');b.disabled=true;b.textContent='提交中...';
    try{
        const r=await fetch('/api/breakfast',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(s)});
        if(r.ok){document.getElementById('form').style.display='none';document.getElementById('ok').style.display='block';}
    }catch(e){alert('提交失败，请重试');b.disabled=false;b.textContent='提交订单';}
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
        :root{--s:#9CAF88;--sd:#7A9568;--n:#1A2A4A;--c:#FAF8F5;--r:#E53E3E}
        body{font-family:-apple-system,sans-serif;background:var(--c);min-height:100vh;padding:20px}
        .ct{max-width:500px;margin:0 auto}
        .hd{background:linear-gradient(135deg,var(--n),#0f1a2e);color:#fff;padding:24px;border-radius:16px;margin-bottom:24px;text-align:center}
        .hd h1{font-size:1.3rem;margin-bottom:4px}
        .hd p{font-size:.85rem;opacity:.7}
        .stats{display:flex;gap:12px;margin-bottom:20px}
        .stat{flex:1;background:#fff;border-radius:12px;padding:16px;text-align:center}
        .stat .num{font-size:1.8rem;font-weight:600;color:var(--n)}
        .stat .lbl{font-size:.75rem;color:#888;margin-top:4px}
        .stat.d .num{color:var(--r)}
        .stat.c .num{color:var(--sd)}
        .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
        .room{background:#fff;border-radius:12px;padding:16px;text-align:center;cursor:pointer;transition:all .2s;border:2px solid transparent}
        .room:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.1)}
        .room.p{border-color:var(--r);background:#fff5f5}
        .room.d{border-color:var(--s);background:#f0fff4}
        .room .rn{font-size:1.3rem;font-weight:600;color:var(--n);margin-bottom:6px}
        .room .rs{font-size:.8rem;padding:4px 10px;border-radius:20px;display:inline-block}
        .room.p .rs{background:rgba(229,62,62,.1);color:var(--r)}
        .room.d .rs{background:rgba(156,175,136,.2);color:var(--sd)}
        .ft{text-align:center;margin-top:24px;font-size:.8rem;color:#aaa}
    </style>
</head>
<body>
<div class="ct">
    <div class="hd"><h1>客房清洁管理</h1><p>小陈家·环洱度假美宿</p></div>
    <div class="stats">
        <div class="stat d"><div class="num" id="pc">0</div><div class="lbl">待打扫</div></div>
        <div class="stat c"><div class="num" id="dc">0</div><div class="lbl">已完成</div></div>
    </div>
    <div class="grid" id="grid"></div>
    <div class="ft">点击房间切换状态</div>
</div>
<script>
let rooms={};
async function load(){
    const r=await fetch('/api/rooms');rooms=await r.json();render();
}
function render(){
    const g=document.getElementById('grid');
    const p=Object.values(rooms).filter(s=>s==='待打扫').length;
    const d=Object.values(rooms).filter(s=>s==='已打扫').length;
    document.getElementById('pc').textContent=p;
    document.getElementById('dc').textContent=d;
    g.innerHTML=Object.entries(rooms).map(([r,s])=>`
        <div class="room ${s==='待打扫'?'p':'d'}" onclick="toggle('${r}')">
            <div class="rn">${r}</div>
            <div class="rs">${s==='待打扫'?'待打扫':'✓'}</div>
        </div>`).join('');
}
async function toggle(room){
    const r=await fetch(`/api/rooms/${room}/toggle`,{method:'POST'});
    if(r.ok){const d=await r.json();rooms[room]=d.status;render();}
}
load();
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
        .hd{background:linear-gradient(135deg,var(--n),#0f1a2e);color:#fff;padding:20px;position:sticky;top:0;z-index:100}
        .hdc{max-width:800px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}
        .hd h1{font-size:1.2rem}
        .st{font-size:.8rem;opacity:.7;display:flex;align-items:center;gap:6px}
        .dot{width:8px;height:8px;background:#48BB78;border-radius:50%;animation:p 2s infinite}
        @keyframes p{0%,100%{opacity:1}50%{opacity:.5}}
        .ct{max-width:800px;margin:0 auto;padding:20px}
        .sec{margin-bottom:24px}
        .sh{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
        .stl{font-size:1rem;color:var(--n);display:flex;align-items:center;gap:8px}
        .stl::before{content:'';width:4px;height:16px;background:var(--s);border-radius:2px}
        .bdg{background:var(--s);color:#fff;padding:4px 10px;border-radius:20px;font-size:.75rem}
        .cd{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.05)}
        .oi{padding:16px 20px;border-bottom:1px solid #f0f0f0;display:flex;justify-content:space-between;align-items:center}
        .oi:last-child{border-bottom:none}
        .ot{font-size:.85rem;color:var(--g);font-weight:500}
        .od{font-size:.85rem;color:#666;margin-top:4px}
        .rg{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;padding:16px}
        .ri{padding:12px 8px;text-align:center;border-radius:8px;font-size:.9rem}
        .ri.p{background:#fff5f5;color:var(--r);font-weight:500}
        .ri.d{background:#f0fff4;color:var(--sd)}
        .ri .rn{font-weight:600;margin-bottom:2px}
        .ri .rs{font-size:.7rem}
        .em{text-align:center;padding:40px 20px;color:#aaa;font-size:.9rem}
        @media(max-width:600px){.rg{grid-template-columns:repeat(4,1fr)}}
    </style>
</head>
<body>
<div class="hd"><div class="hdc"><h1>后台管理</h1><div class="st"><div class="dot"></div><span>实时更新</span></div></div></div>
<div class="ct">
    <div class="sec">
        <div class="sh"><div class="stl">早餐订单</div><div class="bdg" id="oc">0 单</div></div>
        <div class="cd" id="ol"><div class="em">暂无订单</div></div>
    </div>
    <div class="sec">
        <div class="sh"><div class="stl">客房状态</div><div class="bdg" id="pb">0 待打扫</div></div>
        <div class="cd"><div class="rg" id="rg"></div></div>
    </div>
</div>
<script>
async function refresh(){await Promise.all([loadO(),loadR()]);}
async function loadO(){
    try{
        const r=await fetch('/api/breakfast');const o=await r.json();
        document.getElementById('oc').textContent=o.length+' 单';
        if(!o.length){document.getElementById('ol').innerHTML='<div class="em">暂无订单</div>';return;}
        const s=[...o].sort((a,b)=>new Date(b.timestamp)-new Date(a.timestamp));
        document.getElementById('ol').innerHTML=s.map(x=>`
            <div class="oi"><div><div class="ot">${x.time}</div><div class="od">汤底: ${x.soup} | 葱花: ${x.onion} | 香菜: ${x.herb}</div></div></div>`).join('');
    }catch(e){console.error(e);}
}
async function loadR(){
    try{
        const r=await fetch('/api/rooms');const rm=await r.json();
        const p=Object.values(rm).filter(s=>s==='待打扫').length;
        document.getElementById('pb').textContent=p+' 待打扫';
        const s=Object.entries(rm).sort((a,b)=>a[0].localeCompare(b[0]));
        document.getElementById('rg').innerHTML=s.map(([r,st])=>`
            <div class="ri ${st==='待打扫'?'p':'d'}"><div class="rn">${r}</div><div class="rs">${st==='待打扫'?'待打扫':'✓'}</div></div>`).join('');
    }catch(e){console.error(e);}
}
refresh();setInterval(refresh,3000);
</script>
</body></html>'''

# ==================== API路由 ====================

@app.route('/')
def index():
    return '<script>location.href="/breakfast"</script>'

@app.route('/breakfast')
def breakfast_page():
    return BREAKFAST_HTML

@app.route('/cleaning')
def cleaning_page():
    return CLEANING_HTML

@app.route('/admin')
def admin_page():
    return ADMIN_HTML

@app.route('/api/breakfast', methods=['GET'])
def get_breakfast():
    return jsonify(load_json(BREAKFAST_FILE, []))

@app.route('/api/breakfast', methods=['POST'])
def add_breakfast():
    data = request.json
    orders = load_json(BREAKFAST_FILE, [])
    now = datetime.now()
    order = {
        'soup': data.get('soup', ''),
        'onion': data.get('onion', ''),
        'herb': data.get('herb', ''),
        'timestamp': now.isoformat(),
        'time': now.strftime('%H:%M:%S'),
        'date': now.strftime('%Y-%m-%d')
    }
    orders.append(order)
    save_json(BREAKFAST_FILE, orders)
    return jsonify({'success': True})

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    rooms = load_json(ROOMS_FILE, {})
    if not rooms:
        rooms = {room: '待打扫' for room in DEFAULT_ROOMS}
        save_json(ROOMS_FILE, rooms)
    return jsonify(rooms)

@app.route('/api/rooms/<room>/toggle', methods=['POST'])
def toggle_room(room):
    rooms = load_json(ROOMS_FILE, {})
    if room not in rooms:
        return jsonify({'error': '房间不存在'}), 404
    rooms[room] = '已打扫' if rooms[room] == '待打扫' else '待打扫'
    save_json(ROOMS_FILE, rooms)
    return jsonify({'success': True, 'status': rooms[room]})

if __name__ == '__main__':
    print("访问地址:")
    print("  早餐预订: http://localhost:5000/breakfast")
    print("  客房清洁: http://localhost:5000/cleaning")
    print("  后台管理: http://localhost:5000/admin")
    app.run(debug=True, host='0.0.0.0', port=5000)