srd" style="display:none;animation-delay:.2s">
            <div class="card-header">
                <div class="card-num">2</div>
                <div class="card-title">选择份数</div>
            </div>
            <div class="qty-section">
                <div class="qty-label">选择需要的碗数</div>
                <div class="qty-row">
                    <button class="qbtn" onclick="changeQty(-1)">−</button>
                    <span class="qnum" id="qty">1</span>
                    <button class="qbtn" onclick="changeQty(1)">+</button>
                </div>
            </div>
        </div>
        
        <div class="expand" id="bowlArea"></div>
        
        <div id="submitArea" style="display:none;padding:0 0 16px">
            <button class="submit" id="submitBtn" onclick="submitAll()">
                提交全部订单
            </button>
        </div>
    </div>
    
    <div class="success" id="successMsg">
        <div class="success-icon">
            <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <h3>预订成功！</h3>
        <p id="resultMsg"></p>
        <button class="btn-outline" onclick="location.reload()">继续预订</button>
    </div>
    
    <div class="ft">步行5分钟直达洱海S湾</div>
</div>

<script>
const rooms = ['101','201','202','203','204','205','301','302','303','304','305','306'];
let selectedRoom = '';
let bowlCount = 0;
let bowlData = {};

document.getElementById('roomSel').innerHTML = rooms.map((r,i) => 
    `<button class="rbtn" onclick="selectRoom('${r}')" style="animation-delay:${i*0.05}s">${r}</button>`
).join('');

function selectRoom(room) {
    selectedRoom = room;
    document.querySelectorAll('.rbtn').forEach(b => b.classList.remove('sel'));
    event.target.classList.add('sel');
    document.getElementById('qtyCard').style.display = 'block';
    document.getElementById('qtyCard').style.animation = 'bounceIn .4s ease';
    if (bowlCount === 0) changeQty(1);
}

function changeQty(delta) {
    bowlCount = Math.max(1, Math.min(10, bowlCount + delta));
    document.getElementById('qty').textContent = bowlCount;
    document.getElementById('qty').style.animation = 'pulse .3s ease';
    setTimeout(() => document.getElementById('qty').style.animation = '', 300);
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
        <div class="bowl" style="animation-delay:${i*0.1}s">
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
        :root{--s:#9CAF88;--sd:#7A9568;--n:#1A2A4A;--c:#FAF8F5;--g:#C9A961;--r:#E53E3E;--w:#fff}
        body{font-family:-apple-system,'Noto Sans SC',sans-serif;background:linear-gradient(135deg,#f5f0e8 0%,#e8e2d8 100%);min-height:100vh;padding:16px;animation:fadeIn .6s ease}
        @keyframes fadeIn{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
        @keyframes slideDown{from{opacity:0;max-height:0}to{opacity:1;max-height:500px}}
        @keyframes bounceIn{0%{transform:scale(0.9);opacity:0}50%{transform:scale(1.02)}100%{transform:scale(1);opacity:1}}
        @keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}
        .ct{max-width:420px;margin:0 auto}
        .hd{text-align:center;padding:24px 0;animation:fadeIn .8s ease}
        .hd .logo{font-size:2rem;margin-bottom:8px}
        .hd h1{font-size:1.5rem;color:var(--n);margin-bottom:4px;font-weight:600}
        .hd p{font-size:.85rem;color:#888}
        .card{background:var(--w);border-radius:20px;padding:24px;box-shadow:0 4px 20px rgba(0,0,0,.06);transition:all .3s}
        .card:hover{box-shadow:0 8px 30px rgba(0,0,0,.1)}
        .card-header{display:flex;align-items:center;gap:12px;margin-bottom:16px}
        .card-num{width:32px;height:32px;background:linear-gradient(135deg,var(--s),var(--sd));border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:.85rem;font-weight:600}
        .card-title{font-size:1rem;color:var(--n);font-weight:600}
        .rooms{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
        .rbtn{padding:14px 8px;border:2px solid #e8e2d8;border-radius:12px;background:linear-gradient(135deg,var(--w) 0%,var(--c) 100%);font-size:1rem;font-weight:600;cursor:pointer;transition:all .3s cubic-bezier(.4,0,.2,1);text-align:center;font-family:inherit;position:relative;overflow:hidden}
        .rbtn::before{content:'';position:absolute;top:0;left:-100%;width:100%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.4),transparent);transition:left .5s}
        .rbtn:hover::before{left:100%}
        .rbtn:hover{border-color:var(--s);transform:translateY(-2px);box-shadow:0 4px 12px rgba(156,175,136,.3)}
        .rbtn.sel{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border-color:var(--s);animation:pulse .3s ease;box-shadow:0 4px 16px rgba(156,175,136,.4)}
        .expand{overflow:hidden;transition:all .4s cubic-bezier(.4,0,.2,1)}
        .expand.open{animation:slideDown .5s ease forwards}
        .opts{display:flex;gap:12px;padding-top:20px}
        .opt{flex:1;padding:20px 16px;border:2px solid #e8e2d8;border-radius:14px;background:linear-gradient(135deg,var(--w) 0%,var(--c) 100%);font-size:1rem;cursor:pointer;transition:all .3s cubic-bezier(.4,0,.2,1);text-align:center;font-family:inherit;font-weight:600;position:relative;overflow:hidden}
        .opt::before{content:'';position:absolute;top:0;left:-100%;width:100%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.3),transparent);transition:left .5s}
        .opt:hover::before{left:100%}
        .opt:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.1)}
        .opt.yes.sel{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;border-color:var(--s);box-shadow:0 4px 16px rgba(156,175,136,.4)}
        .opt.no.sel{background:linear-gradient(135deg,var(--r),#c53030);color:#fff;border-color:var(--r);box-shadow:0 4px 16px rgba(229,62,62,.4)}
        .submit{width:100%;padding:18px;background:linear-gradient(135deg,var(--g),#b89a4a);color:#fff;border:none;border-radius:14px;font-size:1.05rem;font-weight:600;cursor:pointer;transition:all .3s;font-family:inherit;box-shadow:0 4px 16px rgba(201,169,97,.3);margin-top:20px}
        .submit:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(201,169,97,.4)}
        .submit:active{transform:translateY(0)}
        .submit:disabled{opacity:.4;cursor:not-allowed;transform:none;box-shadow:none}
        .success{text-align:center;padding:40px 20px;display:none;animation:bounceIn .5s ease}
        .success-icon{width:80px;height:80px;background:linear-gradient(135deg,var(--s),var(--sd));border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 20px;animation:pulse 2s infinite}
        .success svg{width:40px;height:40px;stroke:#fff;stroke-width:2;fill:none}
        .success h3{font-size:1.3rem;color:var(--n);margin-bottom:8px}
        .success p{font-size:.9rem;color:#888;margin-bottom:20px}
        .btn-outline{padding:12px 32px;background:transparent;border:2px solid var(--s);color:var(--s);border-radius:10px;cursor:pointer;font-size:.9rem;font-weight:500;transition:all .3s;font-family:inherit}
        .btn-outline:hover{background:var(--s);color:#fff}
        .ft{text-align:center;margin-top:20px;font-size:.7rem;color:#bbb}
    </style>
</head>
<body>
<div class="ct">
    <div class="hd">
        <div class="logo">🛏️</div>
        <h1>客房清洁</h1>
        <p>小陈家·环洱度假美宿</p>
    </div>
    
    <div id="mainForm" class="card">
        <div class="card-header">
            <div class="card-num">1</div>
            <div class="card-title">选择您的房号</div>
        </div>
        <div class="rooms" id="roomSel"></div>
        
        <div class="expand" id="optArea">
            <div class="card-header" style="margin-top:20px">
                <div class="card-num">2</div>
                <div class="card-title">今日是否需要打扫？</div>
            </div>
            <div class="opts">
                <button class="opt yes" onclick="selectOpt('yes')">🧹<br>需要打扫</button>
                <button class="opt no" onclick="selectOpt('no')">🚫<br>免打扰</button>
            </div>
            <button class="submit" id="submitBtn" onclick="submitForm()" disabled>提交</button>
        </div>
    </div>
    
    <div class="success" id="successMsg">
        <div class="success-icon">
            <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <h3>提交成功！</h3>
        <p id="resultMsg"></p>
        <button class="btn-outline" onclick="location.reload()">返回</button>
    </div>
    
    <div class="ft">感谢您的配合</div>
</div>

<script>
const rooms = ['101','201','202','203','204','205','301','302','303','304','305','306'];
let selectedRoom = '';
let selectedOpt = '';

document.getElementById('roomSel').innerHTML = rooms.map((r,i) => 
    `<button class="rbtn" onclick="selectRoom('${r}')" style="animation-delay:${i*0.05}s">${r}</button>`
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
        body{font-family:-apple-system,'Noto Sans SC',sans-serif;background:var(--c);min-height:100vh;animation:fadeIn .6s ease}
        @keyframes fadeIn{from{opacity:0}to{opacity:1}}
        @keyframes slideIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
        .hd{background:linear-gradient(135deg,var(--n) 0%,#0f1a2e 100%);color:#fff;padding:16px 20px;position:sticky;top:0;z-index:100;box-shadow:0 2px 20px rgba(0,0,0,.2)}
        .hdc{max-width:800px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}
        .hd h1{font-size:1.2rem;font-weight:600}
        .st{font-size:.75rem;opacity:.8;display:flex;align-items:center;gap:8px;background:rgba(255,255,255,.1);padding:6px 12px;border-radius:20px}
        .dot{width:8px;height:8px;background:#48BB78;border-radius:50%;animation:pulse 2s infinite}
        @keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(72,187,120,.4)}50%{opacity:.8;box-shadow:0 0 0 6px rgba(72,187,120,0)}}
        .ct{max-width:800px;margin:0 auto;padding:20px}
        .sec{margin-bottom:24px;animation:slideIn .5s ease}
        .sh{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
        .stl{font-size:1rem;color:var(--n);display:flex;align-items:center;gap:10px;font-weight:600}
        .stl::before{content:'';width:4px;height:18px;background:linear-gradient(135deg,var(--s),var(--sd));border-radius:2px}
        .bdg{background:linear-gradient(135deg,var(--s),var(--sd));color:#fff;padding:4px 12px;border-radius:20px;font-size:.75rem;font-weight:600;box-shadow:0 2px 8px rgba(156,175,136,.3)}
        .cd{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,.06)}
        .oi{padding:14px 18px;border-bottom:1px solid #f0f0f0;display:flex;justify-content:space-between;align-items:center;font-size:.9rem;transition:all .2s}
        .oi:last-child{border-bottom:none}
        .oi:hover{background:rgba(156,175,136,.05)}
        .ot{color:var(--g);font-weight:600}
        .od{color:#666}
        .em{text-align:center;padding:40px;color:#aaa;font-size:.9rem}
        .em svg{width:48px;height:48px;stroke:#ddd;stroke-width:1;fill:none;margin-bottom:12px}
    </style>
</head>
<body>
<div class="hd">
    <div class="hdc">
        <h1>后台管理</h1>
        <div class="st"><div class="dot"></div><span>实时更新</span></div>
    </div>
</div>
<div class="ct">
    <div class="sec">
        <div class="sh">
            <div class="stl">早餐订单</div>
            <div class="bdg" id="oc">0</div>
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
            <div class="bdg" id="cc">0</div>
        </div>
        <div class="cd" id="cl">
            <div class="em">
                <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                <p>暂无请求</p>
            </div>
        </div>
    </div>
</div>
<script>
async function refresh(){await Promise.all([loadO(),loadC()]);}
async function loadO(){
    const r=await fetch('/api/breakfast');const o=await r.json();
    document.getElementById('oc').textContent=o.length;
    if(!o.length){document.getElementById('ol').innerHTML='<div class="em"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><p>暂无订单</p></div>';return;}
    const s=[...o].sort((a,b)=>new Date(b.timestamp)-new Date(a.timestamp)).slice(0,30);
    document.getElementById('ol').innerHTML=s.map((x,i)=>`<div class="oi" style="animation:slideIn .3s ease ${i*0.05}s both"><span class="ot">${x.room}房</span><span class="od">汤:${x.soup} 葱:${x.onion} 香:${x.herb}</span><span class="ot">${x.time}</span></div>`).join('');
}
async function loadC(){
    const r=await fetch('/api/cleaning');const c=await r.json();
    document.getElementById('cc').textContent=c.length;
    if(!c.length){document.getElementById('cl').innerHTML='<div class="em"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><p>暂无请求</p></div>';return;}
    const s=[...c].sort((a,b)=>new Date(b.timestamp)-new Date(a.timestamp)).slice(0,20);
    document.getElementById('cl').innerHTML=s.map((x,i)=>`<div class="oi" style="animation:slideIn .3s ease ${i*0.05}s both"><span class="ot">${x.room}房</span><span class="${x.need==='yes'?'od':'ot'}">${x.need==='yes'?'需要打扫':'免打扰'}</span><span class="ot">${x.time}</span></div>`).join('');
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
