#!/usr/bin/env python3
"""
main_api.py - 北斗命數統一 API
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
整合模組：
  • 擇日系統：嫁娶/動土/開市/搬家/安床/祭祀/出行
  • 紫微斗數：排盤/大限/流年
  • 梅花易數：起卦/體用分析
  • 八字分析：四柱/大運/流年
  • 合婚系統：八字合婚
  • 報告生成：完整命理報告
═══════════════════════════════════════════════════════════════════════

XTF Task Chain: A→B→C→D→E
@11星協作：@織明(統籌) @璃語(介面) @理樞(邏輯) @流祇(連結)
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date
from io import BytesIO
import json

# ════════════════════════════════════════════════════════════════════
# 導入各模組
# ════════════════════════════════════════════════════════════════════

# 擇日
from date_base import get_ganzhi_from_date, get_full_rike, get_lunar_info, HAS_LUNAR
from marry_date import MarryDateSelector, DIZHI, SHENGXIAO
from ground_date import GroundDateSelector
from event_date import EventDateSelector, EventType

# 紫微
from ziwei_engine_v1 import create_ziwei_chart, GONG_12

# 梅花
from meihua_engine import full_meihua, GUA_NAME

# 八字
from bazi_base import analyze_bazi, calc_dayun, calc_liunian_simple, HAS_DAYUN

# 合婚
from chart_matching import match_charts

# PDF 報告
from pdf_report_api import (
    DatePDFReport, ZiweiPDFReport, BaziPDFReport, MatchPDFReport,
    EventPDFReport, MeihuaPDFReport,
    HAS_CHINESE_FONT
)

# ════════════════════════════════════════════════════════════════════
# FastAPI App
# ════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="北斗命數 API",
    version="1.0.0",
    description="整合擇日、紫微、梅花、八字、合婚等命理服務"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ════════════════════════════════════════════════════════════════════
# 請求模型
# ════════════════════════════════════════════════════════════════════

class DateSelectRequest(BaseModel):
    event_type: str  # marry/ground/kaishi/banjia/anchuang/jisi/chuxing
    start_date: str
    end_date: str
    owner_year: Optional[int] = None
    man_year: Optional[int] = None
    woman_year: Optional[int] = None
    zuoxiang: Optional[str] = None
    top_n: int = 5

class ZiweiRequest(BaseModel):
    year_gan: str
    year_zhi: str
    lunar_month: int
    lunar_day: int
    hour_zhi: str
    gender: str = "男"

class MeihuaRequest(BaseModel):
    year_zhi_num: int  # 1-12
    lunar_month: int
    lunar_day: int
    hour_zhi_num: int  # 1-12

class BaziRequest(BaseModel):
    year_gz: str
    month_gz: str
    day_gz: str
    hour_gz: str

class DayunRequest(BaseModel):
    year_gz: str
    month_gz: str
    gender: str
    birth_year: int
    birth_month: int
    birth_day: int

class MatchRequest(BaseModel):
    person1: Dict[str, str]
    person2: Dict[str, str]
    match_type: str = "marriage"

# ════════════════════════════════════════════════════════════════════
# 擇日 API
# ════════════════════════════════════════════════════════════════════

@app.post("/api/date/select")
async def select_date(req: DateSelectRequest):
    """統一擇日介面"""
    try:
        start = date.fromisoformat(req.start_date)
        end = date.fromisoformat(req.end_date)
    except:
        raise HTTPException(400, "日期格式錯誤")
    
    results = []
    
    if req.event_type == "marry":
        if not req.man_year or not req.woman_year:
            raise HTTPException(400, "嫁娶需要 man_year 和 woman_year")
        man_zhi = DIZHI[(req.man_year - 4) % 12]
        woman_zhi = DIZHI[(req.woman_year - 4) % 12]
        selector = MarryDateSelector(man_zhi, woman_zhi)
        candidates = selector.select_dates(start, end, req.top_n)
        
        for c in candidates:
            rike = c.full_rike
            results.append({
                "date": str(c.date),
                "ganzhi": c.ganzhi,
                "full_rike": rike.full_rike if rike else "",
                "score": c.score.weighted_total,
                "huangdao": c.huangdao_shen,
                "jianchu": c.jianchu,
            })
        
        return {
            "event_type": "嫁娶",
            "man_sx": selector.man_sx,
            "woman_sx": selector.woman_sx,
            "dali_yue": selector.dali_yue,
            "results": results
        }
    
    elif req.event_type == "ground":
        owner_zhi = DIZHI[(req.owner_year - 4) % 12] if req.owner_year else None
        selector = GroundDateSelector(owner_zhi, zuoxiang=req.zuoxiang)
        candidates = selector.select_dates(start, end, req.top_n)
        
    else:
        event_map = {
            "kaishi": EventType.KAISHI,
            "banjia": EventType.BANJIA,
            "anchuang": EventType.ANCHUANG,
            "jisi": EventType.JISI,
            "chuxing": EventType.CHUXING,
        }
        event_type = event_map.get(req.event_type)
        if not event_type:
            raise HTTPException(400, f"不支援的類型：{req.event_type}")
        
        owner_zhi = DIZHI[(req.owner_year - 4) % 12] if req.owner_year else None
        selector = EventDateSelector(event_type, owner_zhi)
        candidates = selector.select_dates(start, end, req.top_n)
    
    for c in candidates:
        rike = c.full_rike
        results.append({
            "date": str(c.date),
            "ganzhi": c.ganzhi,
            "full_rike": rike.full_rike if rike else "",
            "score": c.score.weighted_total,
            "huangdao": c.huangdao_shen,
            "jianchu": c.jianchu,
        })
    
    return {"event_type": req.event_type, "results": results}

# ════════════════════════════════════════════════════════════════════
# 紫微斗數 API
# ════════════════════════════════════════════════════════════════════

@app.post("/api/ziwei/chart")
async def ziwei_chart(req: ZiweiRequest):
    """紫微斗數排盤"""
    try:
        chart = create_ziwei_chart(
            req.year_gan, req.year_zhi,
            req.lunar_month, req.lunar_day,
            req.hour_zhi, req.gender
        )
    except Exception as e:
        raise HTTPException(400, f"排盤錯誤：{e}")
    
    gongs = []
    for i, gong in enumerate(chart.gongs):
        stars = gong.main_stars + gong.lucky_stars + gong.evil_stars
        gongs.append({
            "index": i,
            "name": gong.name,
            "zhi": gong.zhi,
            "gan": gong.gan,
            "stars": stars,
            "sihua": gong.sihua,
        })
    
    return {
        "ming_gong": GONG_12[chart.ming_gong_idx],
        "shen_gong": GONG_12[chart.shen_gong_idx],
        "ju_shu": chart.ju_shu,
        "gongs": gongs,
    }

# ════════════════════════════════════════════════════════════════════
# 梅花易數 API
# ════════════════════════════════════════════════════════════════════

@app.post("/api/meihua/divine")
async def meihua_divine(req: MeihuaRequest):
    """梅花易數起卦"""
    try:
        result = full_meihua(
            req.year_zhi_num, req.lunar_month,
            req.lunar_day, req.hour_zhi_num
        )
    except Exception as e:
        raise HTTPException(400, f"起卦錯誤：{e}")
    
    ben = result['ben_gua']
    bian = result['bian_gua']
    hu = result['hu_gua']
    ty = result['ti_yong']
    
    return {
        "ben_gua": {
            "upper": GUA_NAME[ben.upper],
            "lower": GUA_NAME[ben.lower],
            "dong_yao": ben.dong_yao,
        },
        "bian_gua": {
            "upper": GUA_NAME[bian.upper],
            "lower": GUA_NAME[bian.lower],
        },
        "hu_gua": {
            "upper": GUA_NAME[hu.upper],
            "lower": GUA_NAME[hu.lower],
        },
        "ti_yong": {
            "ti": ty.ti_name,
            "ti_wx": ty.ti_wx,
            "yong": ty.yong_name,
            "yong_wx": ty.yong_wx,
            "relation": ty.relation,
            "verdict": ty.verdict,
        }
    }

# ════════════════════════════════════════════════════════════════════
# 八字 API
# ════════════════════════════════════════════════════════════════════

@app.post("/api/bazi/analyze")
async def bazi_analyze(req: BaziRequest):
    """八字分析"""
    try:
        chart = analyze_bazi(req.year_gz, req.month_gz, req.day_gz, req.hour_gz)
    except Exception as e:
        raise HTTPException(400, f"分析錯誤：{e}")
    
    return {
        "pillars": {
            "year": req.year_gz,
            "month": req.month_gz,
            "day": req.day_gz,
            "hour": req.hour_gz,
        },
        "day_master": chart.day_master,
        "day_master_wx": chart.day_master_wx,
        "yongshen": chart.yongshen,
        "xishen": chart.xishen,
        "jishen": chart.jishen,
        "shengxiao": chart.shengxiao,
    }

@app.post("/api/bazi/dayun")
async def bazi_dayun(req: DayunRequest):
    """大運計算"""
    if not HAS_DAYUN:
        raise HTTPException(500, "大運模組未啟用")
    
    result = calc_dayun(
        req.year_gz, req.month_gz, req.gender,
        req.birth_year, req.birth_month, req.birth_day
    )
    
    if not result:
        raise HTTPException(400, "大運計算失敗")
    
    dayun_list = []
    for d in result.dayun_list:
        dayun_list.append({
            "order": d.order,
            "ganzhi": d.ganzhi,
            "start_age": d.start_age,
            "end_age": d.end_age,
        })
    
    return {
        "qiyun_age": result.qiyun_age,
        "direction": result.direction,
        "dayun_list": dayun_list,
    }

@app.post("/api/bazi/liunian")
async def bazi_liunian(req: BaziRequest, year: int):
    """流年分析"""
    if not HAS_DAYUN:
        raise HTTPException(500, "流年模組未啟用")
    
    bazi = (req.year_gz, req.month_gz, req.day_gz, req.hour_gz)
    result = calc_liunian_simple(bazi, year)
    
    if not result:
        raise HTTPException(400, "流年計算失敗")
    
    return {
        "year": year,
        "ganzhi": result.ganzhi,
        "gan_shishen": result.gan_shishen,
        "tendency": result.tendency,
        "interactions": result.interactions,
    }

# ════════════════════════════════════════════════════════════════════
# 合婚 API
# ════════════════════════════════════════════════════════════════════

@app.post("/api/match")
async def chart_match(req: MatchRequest):
    """合婚分析"""
    try:
        result = match_charts(req.person1, req.person2, req.match_type)
    except Exception as e:
        raise HTTPException(400, f"合婚錯誤：{e}")
    
    return result

# ════════════════════════════════════════════════════════════════════
# 工具 API
# ════════════════════════════════════════════════════════════════════

@app.get("/api/utils/ganzhi/{date_str}")
async def get_ganzhi(date_str: str):
    """查詢日期干支"""
    try:
        d = date.fromisoformat(date_str)
    except:
        raise HTTPException(400, "日期格式錯誤")
    
    year_gz, month_gz, day_gz = get_ganzhi_from_date(d)
    rike = get_full_rike(d)
    lunar = get_lunar_info(d)
    
    return {
        "date": str(d),
        "year_gz": year_gz,
        "month_gz": month_gz,
        "day_gz": day_gz,
        "hour_gz": rike.hour_gz,
        "full_rike": rike.full_rike,
        "lunar": lunar,
    }

@app.get("/api/status")
async def status():
    """系統狀態"""
    return {
        "version": "1.0.0",
        "modules": {
            "lunar": HAS_LUNAR,
            "dayun": HAS_DAYUN,
            "ziwei": True,
            "meihua": True,
            "matching": True,
            "pdf": HAS_CHINESE_FONT,
        }
    }

# ════════════════════════════════════════════════════════════════════
# PDF 下載 API
# ════════════════════════════════════════════════════════════════════

class PDFMarryRequest(BaseModel):
    man_year: int
    woman_year: int
    start_date: str
    end_date: str
    top_n: int = 5

class PDFGroundRequest(BaseModel):
    owner_year: int
    start_date: str
    end_date: str
    zuoxiang: Optional[str] = None
    top_n: int = 5

class PDFEventRequest(BaseModel):
    event_type: str
    start_date: str
    end_date: str
    owner_year: Optional[int] = None
    top_n: int = 5

@app.post("/api/pdf/marry")
async def download_marry_pdf(req: PDFMarryRequest):
    """下載嫁娶擇日 PDF"""
    try:
        start = date.fromisoformat(req.start_date)
        end = date.fromisoformat(req.end_date)
    except:
        raise HTTPException(400, "日期格式錯誤")
    
    from datetime import datetime
    gen = DatePDFReport()
    pdf_bytes = gen.generate_marry(req.man_year, req.woman_year, start, end, req.top_n)
    
    filename = f"marry_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/api/pdf/ground")
async def download_ground_pdf(req: PDFGroundRequest):
    """下載動土擇日 PDF"""
    try:
        start = date.fromisoformat(req.start_date)
        end = date.fromisoformat(req.end_date)
    except:
        raise HTTPException(400, "日期格式錯誤")
    
    from datetime import datetime
    gen = DatePDFReport()
    pdf_bytes = gen.generate_ground(req.owner_year, start, end, req.zuoxiang, req.top_n)
    
    filename = f"ground_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/api/pdf/ziwei")
async def download_ziwei_pdf(req: ZiweiRequest):
    """下載紫微命盤 PDF"""
    from datetime import datetime
    gen = ZiweiPDFReport()
    pdf_bytes = gen.generate(
        req.year_gan, req.year_zhi,
        req.lunar_month, req.lunar_day,
        req.hour_zhi, req.gender
    )
    
    filename = f"ziwei_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/api/pdf/bazi")
async def download_bazi_pdf(req: DayunRequest):
    """下載八字分析 PDF"""
    from datetime import datetime
    gen = BaziPDFReport()
    pdf_bytes = gen.generate(
        req.year_gz, req.month_gz, req.year_gz[:2], req.month_gz[:2],  # 簡化
        req.birth_year, req.birth_month, req.birth_day, req.gender
    )
    
    filename = f"bazi_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/api/pdf/match")
async def download_match_pdf(req: MatchRequest):
    """下載合婚分析 PDF"""
    from datetime import datetime
    gen = MatchPDFReport()
    pdf_bytes = gen.generate(req.person1, req.person2, req.match_type)
    
    filename = f"match_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/api/pdf/event")
async def download_event_pdf(req: PDFEventRequest):
    """下載多用途擇日 PDF（開市/搬家/安床/祭祀/出行）"""
    from datetime import datetime
    try:
        start = date.fromisoformat(req.start_date)
        end = date.fromisoformat(req.end_date)
    except:
        raise HTTPException(400, "日期格式錯誤")
    
    gen = EventPDFReport()
    pdf_bytes = gen.generate(req.event_type, start, end, req.owner_year, req.top_n)
    
    filename = f"{req.event_type}_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

class MeihuaPDFRequest(BaseModel):
    year_zhi_num: int
    lunar_month: int
    lunar_day: int
    hour_zhi_num: int
    question: Optional[str] = None

@app.post("/api/pdf/meihua")
async def download_meihua_pdf(req: MeihuaPDFRequest):
    """下載梅花易數 PDF"""
    from datetime import datetime
    gen = MeihuaPDFReport()
    pdf_bytes = gen.generate(
        req.year_zhi_num, req.lunar_month,
        req.lunar_day, req.hour_zhi_num,
        req.question
    )
    
    filename = f"meihua_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ════════════════════════════════════════════════════════════════════
# 前端介面
# ════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>北斗命數系統</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            color: #eee; min-height: 100vh; padding: 20px;
        }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; font-size: 2.2em;
            background: linear-gradient(90deg, #ffd700, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
        .card {
            background: rgba(255,255,255,0.05); border-radius: 15px;
            padding: 25px; backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card:hover { transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .card h2 { font-size: 1.3em; margin-bottom: 15px; color: #ffd700; }
        .card p { color: #aaa; font-size: 0.95em; line-height: 1.6; }
        .card .icon { font-size: 2.5em; margin-bottom: 15px; }
        .endpoint { background: rgba(0,0,0,0.3); padding: 8px 12px; border-radius: 6px;
            font-family: monospace; font-size: 0.85em; margin-top: 15px; color: #4ecdc4; }
        .status { text-align: center; margin-top: 30px; padding: 15px;
            background: rgba(78,205,196,0.1); border-radius: 10px; }
        .status span { margin: 0 10px; }
        .on { color: #2ecc71; }
        .off { color: #e74c3c; }
        footer { text-align: center; margin-top: 40px; color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌟 北斗命數系統</h1>
        
        <div class="grid">
            <div class="card">
                <div class="icon">📅</div>
                <h2>擇日系統</h2>
                <p>嫁娶、動土、開市、搬家、安床、祭祀、出行</p>
                <div class="endpoint">POST /api/date/select</div>
            </div>
            
            <div class="card">
                <div class="icon">⭐</div>
                <h2>紫微斗數</h2>
                <p>命盤排盤、十二宮、四化、大限流年</p>
                <div class="endpoint">POST /api/ziwei/chart</div>
            </div>
            
            <div class="card">
                <div class="icon">🌸</div>
                <h2>梅花易數</h2>
                <p>先天起卦、本變互卦、體用分析</p>
                <div class="endpoint">POST /api/meihua/divine</div>
            </div>
            
            <div class="card">
                <div class="icon">🔮</div>
                <h2>八字分析</h2>
                <p>四柱八字、用神喜忌、大運流年</p>
                <div class="endpoint">POST /api/bazi/analyze</div>
            </div>
            
            <div class="card">
                <div class="icon">💑</div>
                <h2>合婚分析</h2>
                <p>八字合婚、親子配對、合作分析</p>
                <div class="endpoint">POST /api/match</div>
            </div>
            
            <div class="card">
                <div class="icon">🛠️</div>
                <h2>工具</h2>
                <p>干支查詢、農曆轉換、日課計算</p>
                <div class="endpoint">GET /api/utils/ganzhi/{date}</div>
            </div>
            
            <div class="card">
                <div class="icon">📄</div>
                <h2>PDF 報告</h2>
                <p>擇日/紫微/八字/合婚 PDF 下載</p>
                <div class="endpoint">POST /api/pdf/*</div>
            </div>
        </div>
        
        <div class="status" id="status">
            載入中...
        </div>
        
        <footer>
            北斗命數 v1.0.0 | XTF Task Chain | @11星協作
        </footer>
    </div>
    
    <script>
        fetch('/api/status')
            .then(r => r.json())
            .then(d => {
                const m = d.modules;
                document.getElementById('status').innerHTML = `
                    <span class="${m.lunar ? 'on' : 'off'}">農曆 ${m.lunar ? '✓' : '✗'}</span>
                    <span class="${m.dayun ? 'on' : 'off'}">大運 ${m.dayun ? '✓' : '✗'}</span>
                    <span class="${m.ziwei ? 'on' : 'off'}">紫微 ${m.ziwei ? '✓' : '✗'}</span>
                    <span class="${m.meihua ? 'on' : 'off'}">梅花 ${m.meihua ? '✓' : '✗'}</span>
                    <span class="${m.matching ? 'on' : 'off'}">合婚 ${m.matching ? '✓' : '✗'}</span>
                `;
            });
    </script>
</body>
</html>
    """

# ════════════════════════════════════════════════════════════════════
# 啟動
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    print("🌟 北斗命數系統啟動中...")
    print("   http://localhost:8000")
    print("   API 文檔：http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
