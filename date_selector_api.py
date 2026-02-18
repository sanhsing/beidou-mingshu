#!/usr/bin/env python3
"""
date_selector_api.py - 擇日系統 API
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
API 端點：
  POST /api/date/marry     嫁娶擇日
  POST /api/date/ground    動土擇日
  POST /api/date/event     多用途擇日
  GET  /api/date/full      完整日課查詢
  GET  /                   前端介面
═══════════════════════════════════════════════════════════════════════

PYLIB 依賴：date_base.py, marry_date.py, ground_date.py, event_date.py
@11星協作：@璃語(介面) @織明(API) @流祇(連結)
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import json

# 導入擇日模組
from date_base import get_ganzhi_from_date, get_full_rike, get_lunar_info, HAS_LUNAR
from marry_date import MarryDateSelector, DIZHI, SHENGXIAO
from ground_date import GroundDateSelector
from event_date import EventDateSelector, EventType

# ════════════════════════════════════════════════════════════════════
# FastAPI App
# ════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="北斗擇日系統 API",
    version="1.0.0",
    description="嫁娶/動土/開市/搬家/安床/祭祀/出行 擇日服務"
)

# ════════════════════════════════════════════════════════════════════
# 請求模型
# ════════════════════════════════════════════════════════════════════

class MarryRequest(BaseModel):
    man_year: int           # 男方出生年
    woman_year: int         # 女方出生年
    start_date: str         # 開始日期 YYYY-MM-DD
    end_date: str           # 結束日期 YYYY-MM-DD
    top_n: int = 5

class GroundRequest(BaseModel):
    owner_year: int         # 屋主出生年
    start_date: str
    end_date: str
    zuoxiang: Optional[str] = None  # 坐向
    owner_bazi: Optional[List[str]] = None  # 完整八字
    top_n: int = 5

class EventRequest(BaseModel):
    event_type: str         # 開市/搬家/安床/祭祀/出行
    owner_year: Optional[int] = None
    start_date: str
    end_date: str
    top_n: int = 5

class DateQueryRequest(BaseModel):
    date: str               # YYYY-MM-DD

# ════════════════════════════════════════════════════════════════════
# 回應模型
# ════════════════════════════════════════════════════════════════════

class DateResult(BaseModel):
    date: str
    ganzhi: str
    lunar: str
    full_rike: str
    huangdao: str
    jianchu: str
    xiu: str
    chong_sha: str
    score: float
    jishi: List[str]
    ji_shen: List[str]
    xiong_shen: List[str]

class MarryResponse(BaseModel):
    man_sx: str
    woman_sx: str
    dali_yue: List[int]
    xiaoli_yue: List[int]
    results: List[DateResult]

class GroundResponse(BaseModel):
    owner_sx: str
    zuoxiang: Optional[str]
    results: List[DateResult]

class EventResponse(BaseModel):
    event_type: str
    results: List[DateResult]

class FullRikeResponse(BaseModel):
    date: str
    year_gz: str
    month_gz: str
    day_gz: str
    hour_gz: str
    full_rike: str
    lunar: Optional[dict]
    jishi: List[dict]

# ════════════════════════════════════════════════════════════════════
# API 端點
# ════════════════════════════════════════════════════════════════════

@app.post("/api/date/marry", response_model=MarryResponse)
async def marry_date(req: MarryRequest):
    """嫁娶擇日"""
    try:
        start = date.fromisoformat(req.start_date)
        end = date.fromisoformat(req.end_date)
    except:
        raise HTTPException(400, "日期格式錯誤，請使用 YYYY-MM-DD")
    
    man_zhi = DIZHI[(req.man_year - 4) % 12]
    woman_zhi = DIZHI[(req.woman_year - 4) % 12]
    
    selector = MarryDateSelector(man_zhi, woman_zhi)
    candidates = selector.select_dates(start, end, req.top_n)
    
    results = []
    for c in candidates:
        rike = c.full_rike
        results.append(DateResult(
            date=str(c.date),
            ganzhi=c.ganzhi,
            lunar=c.lunar,
            full_rike=rike.full_rike if rike else "",
            huangdao=c.huangdao_shen,
            jianchu=c.jianchu,
            xiu=c.xiu,
            chong_sha=f"沖{c.chong_sx}煞{c.sha_fang}",
            score=c.score.weighted_total,
            jishi=[gz for _, gz, _ in (rike.jishi_list if rike else [])[:4]],
            ji_shen=c.marry_ji_shen,
            xiong_shen=c.marry_xiong_shen
        ))
    
    return MarryResponse(
        man_sx=selector.man_sx,
        woman_sx=selector.woman_sx,
        dali_yue=selector.dali_yue,
        xiaoli_yue=selector.xiaoli_yue,
        results=results
    )

@app.post("/api/date/ground", response_model=GroundResponse)
async def ground_date(req: GroundRequest):
    """動土擇日"""
    try:
        start = date.fromisoformat(req.start_date)
        end = date.fromisoformat(req.end_date)
    except:
        raise HTTPException(400, "日期格式錯誤")
    
    owner_zhi = DIZHI[(req.owner_year - 4) % 12]
    owner_bazi = tuple(req.owner_bazi) if req.owner_bazi else None
    
    selector = GroundDateSelector(
        owner_zhi,
        zuoxiang=req.zuoxiang,
        owner_bazi=owner_bazi
    )
    candidates = selector.select_dates(start, end, req.top_n)
    
    results = []
    for c in candidates:
        rike = c.full_rike
        results.append(DateResult(
            date=str(c.date),
            ganzhi=c.ganzhi,
            lunar=c.lunar,
            full_rike=rike.full_rike if rike else "",
            huangdao=c.huangdao_shen,
            jianchu=c.jianchu,
            xiu=c.xiu,
            chong_sha=f"沖{c.chong_sx}煞{c.sha_fang}",
            score=c.score.weighted_total,
            jishi=[gz for _, gz, _ in (rike.jishi_list if rike else [])[:4]],
            ji_shen=c.ground_ji_shen,
            xiong_shen=c.ground_xiong_shen
        ))
    
    return GroundResponse(
        owner_sx=selector.owner_sx,
        zuoxiang=req.zuoxiang,
        results=results
    )

@app.post("/api/date/event", response_model=EventResponse)
async def event_date(req: EventRequest):
    """多用途擇日"""
    try:
        start = date.fromisoformat(req.start_date)
        end = date.fromisoformat(req.end_date)
    except:
        raise HTTPException(400, "日期格式錯誤")
    
    # 解析用途類型
    event_map = {
        "開市": EventType.KAISHI,
        "搬家": EventType.BANJIA,
        "安床": EventType.ANCHUANG,
        "祭祀": EventType.JISI,
        "出行": EventType.CHUXING,
    }
    event_type = event_map.get(req.event_type)
    if not event_type:
        raise HTTPException(400, f"不支援的用途類型：{req.event_type}")
    
    owner_zhi = DIZHI[(req.owner_year - 4) % 12] if req.owner_year else None
    
    selector = EventDateSelector(event_type, owner_zhi)
    candidates = selector.select_dates(start, end, req.top_n)
    
    results = []
    for c in candidates:
        rike = c.full_rike
        results.append(DateResult(
            date=str(c.date),
            ganzhi=c.ganzhi,
            lunar=c.lunar,
            full_rike=rike.full_rike if rike else "",
            huangdao=c.huangdao_shen,
            jianchu=c.jianchu,
            xiu=c.xiu,
            chong_sha=f"沖{c.chong_sx}煞{c.sha_fang}",
            score=c.score.weighted_total,
            jishi=[gz for _, gz, _ in (rike.jishi_list if rike else [])[:4]],
            ji_shen=c.event_ji_shen,
            xiong_shen=c.event_xiong_shen
        ))
    
    return EventResponse(
        event_type=req.event_type,
        results=results
    )

@app.get("/api/date/full/{date_str}", response_model=FullRikeResponse)
async def get_full_date(date_str: str):
    """查詢完整日課"""
    try:
        d = date.fromisoformat(date_str)
    except:
        raise HTTPException(400, "日期格式錯誤")
    
    rike = get_full_rike(d)
    lunar = get_lunar_info(d)
    
    return FullRikeResponse(
        date=str(d),
        year_gz=rike.year_gz,
        month_gz=rike.month_gz,
        day_gz=rike.day_gz,
        hour_gz=rike.hour_gz,
        full_rike=rike.full_rike,
        lunar=lunar,
        jishi=[{"zhi": z, "gz": gz, "score": s} for z, gz, s in rike.jishi_list[:6]]
    )

# ════════════════════════════════════════════════════════════════════
# 前端介面
# ════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def index():
    """前端頁面"""
    return """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>北斗擇日系統</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { 
            text-align: center; 
            margin-bottom: 30px;
            font-size: 2em;
            background: linear-gradient(90deg, #ffd700, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h2 { 
            margin-bottom: 20px;
            font-size: 1.3em;
            color: #ffd700;
        }
        .form-row { display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 15px; }
        .form-group { flex: 1; min-width: 150px; }
        label { display: block; margin-bottom: 5px; font-size: 0.9em; color: #aaa; }
        input, select {
            width: 100%;
            padding: 10px 15px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 1em;
        }
        input:focus, select:focus { outline: none; border-color: #ffd700; }
        button {
            background: linear-gradient(90deg, #ffd700, #ff6b6b);
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            color: #000;
            font-weight: bold;
            cursor: pointer;
            font-size: 1em;
            transition: transform 0.2s;
        }
        button:hover { transform: scale(1.02); }
        .results { margin-top: 20px; }
        .result-item {
            background: rgba(255,255,255,0.03);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #ffd700;
        }
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .result-date { font-size: 1.3em; font-weight: bold; }
        .result-score {
            background: linear-gradient(90deg, #ffd700, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.2em;
            font-weight: bold;
        }
        .result-rike {
            background: rgba(255,215,0,0.1);
            padding: 12px 15px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 1.1em;
            margin-bottom: 15px;
            text-align: center;
        }
        .result-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
        .result-cell { 
            background: rgba(0,0,0,0.2);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.9em;
        }
        .result-cell span { color: #aaa; }
        .jishi { color: #4ecdc4; }
        .ji { color: #2ecc71; }
        .xiong { color: #e74c3c; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab {
            padding: 10px 20px;
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            cursor: pointer;
            transition: all 0.2s;
        }
        .tab.active { background: linear-gradient(90deg, #ffd700, #ff6b6b); color: #000; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌟 北斗擇日系統</h1>
        
        <div class="tabs">
            <div class="tab active" onclick="showTab('marry')">💒 嫁娶</div>
            <div class="tab" onclick="showTab('ground')">🏗️ 動土</div>
            <div class="tab" onclick="showTab('event')">📅 其他</div>
        </div>
        
        <!-- 嫁娶擇日 -->
        <div id="marry" class="tab-content active">
            <div class="card">
                <h2>💒 嫁娶擇日</h2>
                <div class="form-row">
                    <div class="form-group">
                        <label>男方出生年</label>
                        <input type="number" id="man_year" value="1990" min="1940" max="2020">
                    </div>
                    <div class="form-group">
                        <label>女方出生年</label>
                        <input type="number" id="woman_year" value="1992" min="1940" max="2020">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>開始日期</label>
                        <input type="date" id="marry_start" value="2026-03-01">
                    </div>
                    <div class="form-group">
                        <label>結束日期</label>
                        <input type="date" id="marry_end" value="2026-03-31">
                    </div>
                </div>
                <button onclick="searchMarry()">查詢嫁娶吉日</button>
                <div id="marry_results" class="results"></div>
            </div>
        </div>
        
        <!-- 動土擇日 -->
        <div id="ground" class="tab-content">
            <div class="card">
                <h2>🏗️ 動土擇日</h2>
                <div class="form-row">
                    <div class="form-group">
                        <label>屋主出生年</label>
                        <input type="number" id="owner_year" value="1985" min="1940" max="2020">
                    </div>
                    <div class="form-group">
                        <label>坐向（可選）</label>
                        <select id="zuoxiang">
                            <option value="">不指定</option>
                            <option value="坐北朝南">坐北朝南</option>
                            <option value="坐南朝北">坐南朝北</option>
                            <option value="坐東朝西">坐東朝西</option>
                            <option value="坐西朝東">坐西朝東</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>開始日期</label>
                        <input type="date" id="ground_start" value="2026-03-01">
                    </div>
                    <div class="form-group">
                        <label>結束日期</label>
                        <input type="date" id="ground_end" value="2026-03-31">
                    </div>
                </div>
                <button onclick="searchGround()">查詢動土吉日</button>
                <div id="ground_results" class="results"></div>
            </div>
        </div>
        
        <!-- 其他用途 -->
        <div id="event" class="tab-content">
            <div class="card">
                <h2>📅 多用途擇日</h2>
                <div class="form-row">
                    <div class="form-group">
                        <label>用途類型</label>
                        <select id="event_type">
                            <option value="開市">開市</option>
                            <option value="搬家">搬家</option>
                            <option value="安床">安床</option>
                            <option value="祭祀">祭祀</option>
                            <option value="出行">出行</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>事主出生年（可選）</label>
                        <input type="number" id="event_owner_year" placeholder="可不填">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>開始日期</label>
                        <input type="date" id="event_start" value="2026-03-01">
                    </div>
                    <div class="form-group">
                        <label>結束日期</label>
                        <input type="date" id="event_end" value="2026-03-31">
                    </div>
                </div>
                <button onclick="searchEvent()">查詢吉日</button>
                <div id="event_results" class="results"></div>
            </div>
        </div>
    </div>
    
    <script>
        function showTab(name) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.querySelector(`.tab[onclick="showTab('${name}')"]`).classList.add('active');
            document.getElementById(name).classList.add('active');
        }
        
        function renderResults(results, container) {
            if (!results.length) {
                container.innerHTML = '<p style="text-align:center;color:#aaa;">無符合條件的吉日</p>';
                return;
            }
            
            container.innerHTML = results.map((r, i) => `
                <div class="result-item">
                    <div class="result-header">
                        <span class="result-date">#${i+1} ${r.date} ${r.ganzhi}</span>
                        <span class="result-score">${r.score.toFixed(0)} 分</span>
                    </div>
                    <div class="result-rike">📅 ${r.full_rike}</div>
                    <div class="result-grid">
                        <div class="result-cell"><span>黃道</span> ${r.huangdao}</div>
                        <div class="result-cell"><span>建除</span> ${r.jianchu}</div>
                        <div class="result-cell"><span>二十八宿</span> ${r.xiu}</div>
                        <div class="result-cell"><span>沖煞</span> ${r.chong_sha}</div>
                        <div class="result-cell jishi"><span>吉時</span> ${r.jishi.join(' ')}</div>
                        ${r.ji_shen.length ? `<div class="result-cell ji"><span>吉神</span> ${r.ji_shen.join(' ')}</div>` : ''}
                        ${r.xiong_shen.length ? `<div class="result-cell xiong"><span>凶神</span> ${r.xiong_shen.join(' ')}</div>` : ''}
                    </div>
                </div>
            `).join('');
        }
        
        async function searchMarry() {
            const data = {
                man_year: parseInt(document.getElementById('man_year').value),
                woman_year: parseInt(document.getElementById('woman_year').value),
                start_date: document.getElementById('marry_start').value,
                end_date: document.getElementById('marry_end').value,
                top_n: 5
            };
            
            const res = await fetch('/api/date/marry', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const json = await res.json();
            
            const container = document.getElementById('marry_results');
            container.innerHTML = `<p style="margin-bottom:15px;">
                男方：${json.man_sx} | 女方：${json.woman_sx}<br>
                大利月：${json.dali_yue.join(', ')} 月 | 小利月：${json.xiaoli_yue.join(', ')} 月
            </p>`;
            renderResults(json.results, container);
        }
        
        async function searchGround() {
            const data = {
                owner_year: parseInt(document.getElementById('owner_year').value),
                zuoxiang: document.getElementById('zuoxiang').value || null,
                start_date: document.getElementById('ground_start').value,
                end_date: document.getElementById('ground_end').value,
                top_n: 5
            };
            
            const res = await fetch('/api/date/ground', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const json = await res.json();
            
            const container = document.getElementById('ground_results');
            container.innerHTML = `<p style="margin-bottom:15px;">
                屋主：${json.owner_sx} ${json.zuoxiang ? '| 坐向：' + json.zuoxiang : ''}
            </p>`;
            renderResults(json.results, container);
        }
        
        async function searchEvent() {
            const ownerYear = document.getElementById('event_owner_year').value;
            const data = {
                event_type: document.getElementById('event_type').value,
                owner_year: ownerYear ? parseInt(ownerYear) : null,
                start_date: document.getElementById('event_start').value,
                end_date: document.getElementById('event_end').value,
                top_n: 5
            };
            
            const res = await fetch('/api/date/event', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const json = await res.json();
            
            const container = document.getElementById('event_results');
            container.innerHTML = `<p style="margin-bottom:15px;">用途：${json.event_type}</p>`;
            renderResults(json.results, container);
        }
    </script>
</body>
</html>
    """

# ════════════════════════════════════════════════════════════════════
# 啟動
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    print("🌟 北斗擇日系統啟動中...")
    print("   http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
