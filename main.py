#!/usr/bin/env python3
"""
北斗命數 Web API v1.0 (MVP 部署版)
===================================
XTF: 整合部署 | 執行星: 星殼(架構)+璃語(介面)

📚 認識論聲明：
術數是個人化決策框架生成器，與天氣預報同構
— 提供機率性參考，不做命定式裁決
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import sqlite3
import os

# ===== 引入可用引擎 =====
from lunar_calendar_v2 import solar_to_lunar, get_bazi, get_hour_ganzhi
from ziwei_engine_v1 import create_ziwei_chart
from qimen_engine_v1 import create_qimen_pan, analyze_geju, field_translation
from name_engine import calculate_wuge

# 天干地支定義
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
GAN_WX = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
          "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}

# ===== 康熙筆畫查詢 =====
KANGXI_DB = os.path.join(os.path.dirname(__file__), "kangxi_20k.db")

def get_kangxi_strokes(char: str) -> Optional[int]:
    try:
        conn = sqlite3.connect(KANGXI_DB)
        cur = conn.cursor()
        cur.execute("SELECT strokes FROM kangxi WHERE character = ?", (char,))
        result = cur.fetchone()
        conn.close()
        return result[0] if result else None
    except:
        return None

def get_name_strokes(name: str) -> Dict[str, int]:
    return {c: get_kangxi_strokes(c) or 0 for c in name}

# ===== FastAPI App =====
app = FastAPI(
    title="北斗命數 API",
    description="古法是根，場論是枝，用戶是花",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 資料模型 =====
class BirthInfo(BaseModel):
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int = Field(12, ge=0, le=23)
    gender: str = Field("男")
    name: Optional[str] = None

class NameQuery(BaseModel):
    surname: str = Field(..., min_length=1, max_length=2)
    given_name: str = Field(..., min_length=1, max_length=3)

class MeihuaQuery(BaseModel):
    upper_num: int = Field(..., ge=1)
    lower_num: int = Field(..., ge=1)
    dong_yao: int = Field(..., ge=1, le=6)
    question: Optional[str] = None

class APIResponse(BaseModel):
    success: bool
    engine: str
    version: str = "1.0"
    data: Dict[str, Any]
    source_tag: str
    disclaimer: str = "術數為決策參考框架，非命定裁決。趨吉避凶——趨和避都是動詞，主語是人。"

# ===== 路由 =====
@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/info")
async def api_info():
    return {
        "name": "北斗命數 API",
        "version": "1.0.0",
        "engines": ["八字", "紫微斗數", "姓名學", "梅花易數", "奇門遁甲"],
        "philosophy": "古法是根，場論是枝，用戶是花",
    }

# 農曆轉換
@app.get("/api/v1/lunar/{year}/{month}/{day}")
async def convert_lunar(year: int, month: int, day: int):
    try:
        lunar = solar_to_lunar(year, month, day)
        return APIResponse(
            success=True, engine="農曆轉換",
            data={
                "solar": f"{year}/{month}/{day}",
                "lunar": str(lunar),
                "year_ganzhi": f"{lunar.year_gan}{lunar.year_zhi}",
                "month_ganzhi": f"{lunar.month_gan}{lunar.month_zhi}",
                "day_ganzhi": f"{lunar.day_gan}{lunar.day_zhi}",
                "shengxiao": lunar.shengxiao,
            },
            source_tag="📜萬年曆",
        )
    except Exception as e:
        raise HTTPException(400, str(e))

# 八字分析
@app.post("/api/v1/bazi")
async def analyze_bazi_api(info: BirthInfo):
    try:
        bazi = get_bazi(info.year, info.month, info.day, info.hour)
        lunar = bazi["lunar"]
        
        return APIResponse(
            success=True, engine="八字命理",
            data={
                "birth": {"solar": f"{info.year}/{info.month}/{info.day} {info.hour}:00", "lunar": str(lunar), "shengxiao": lunar.shengxiao},
                "bazi": bazi["bazi_str"],
                "pillars": {"year": bazi["year"], "month": bazi["month"], "day": bazi["day"], "hour": bazi["hour"]},
                "day_master": lunar.day_gan,
                "day_element": GAN_WX.get(lunar.day_gan, ""),
            },
            source_tag="📜《三命通會》《滴天髓》",
        )
    except Exception as e:
        raise HTTPException(400, str(e))

# 紫微斗數
@app.post("/api/v1/ziwei")
async def analyze_ziwei_api(info: BirthInfo):
    try:
        lunar = solar_to_lunar(info.year, info.month, info.day)
        hour_zhi = DIZHI[((info.hour + 1) // 2) % 12]
        
        chart = create_ziwei_chart(lunar.year_gan, lunar.year_zhi, lunar.month, lunar.day, hour_zhi, info.gender)
        
        gongs = {}
        for g in chart.gongs:
            gongs[g.name] = {"zhi": g.zhi, "main_stars": g.main_stars, "lucky_stars": g.lucky_stars, "sihua": g.sihua}
        
        return APIResponse(
            success=True, engine="紫微斗數",
            data={
                "lunar": str(lunar),
                "ju_shu": chart.ju_shu,
                "ming_gong": chart.gongs[chart.ming_gong_idx].name,
                "ming_stars": chart.gongs[chart.ming_gong_idx].main_stars,
                "shen_gong": chart.gongs[chart.shen_gong_idx].name,
                "shen_stars": chart.gongs[chart.shen_gong_idx].main_stars,
                "sihua": chart.sihua_stars,
                "gongs": gongs,
            },
            source_tag="📜《紫微斗數全書》",
        )
    except Exception as e:
        raise HTTPException(400, str(e))

# 姓名學
@app.post("/api/v1/name")
async def analyze_name_api(query: NameQuery):
    try:
        full_name = query.surname + query.given_name
        strokes = get_name_strokes(full_name)
        
        result = calculate_wuge(query.surname, list(query.given_name), strokes)
        
        return APIResponse(
            success=True, engine="姓名學",
            data={
                "name": full_name,
                "strokes": strokes,
                "total": sum(strokes.values()),
                "wuge": {"tian": result.tian, "ren": result.ren, "di": result.di, "wai": result.wai, "zong": result.zong},
                "sancai": result.sancai_str,
            },
            source_tag="📐《康熙字典》+ 熊崎氏",
        )
    except Exception as e:
        raise HTTPException(400, str(e))

# 梅花易數（簡化版）
@app.post("/api/v1/meihua")
async def analyze_meihua_api(query: MeihuaQuery):
    try:
        BAGUA = ["乾", "兌", "離", "震", "巽", "坎", "艮", "坤"]
        upper = BAGUA[(query.upper_num - 1) % 8]
        lower = BAGUA[(query.lower_num - 1) % 8]
        
        return APIResponse(
            success=True, engine="梅花易數",
            data={
                "upper_gua": upper,
                "lower_gua": lower,
                "dong_yao": query.dong_yao,
                "question": query.question,
                "hint": "卦象僅供參考，詳細解讀需結合具體情境",
            },
            source_tag="📜《梅花易數》",
        )
    except Exception as e:
        raise HTTPException(400, str(e))

# 奇門遁甲
@app.post("/api/v1/qimen")
async def analyze_qimen_api(info: BirthInfo):
    try:
        lunar = solar_to_lunar(info.year, info.month, info.day)
        pan = create_qimen_pan(info.year, info.month, info.day, info.hour, lunar.day_gan)
        geju = analyze_geju(pan)
        
        gongs = {}
        for num, g in pan.gongs.items():
            gongs[g.gong_name] = {"direction": g.direction, "dipan": g.dipan_gan, "tianpan": g.tianpan_gan, "men": g.men, "xing": g.xing, "shen": g.shen}
        
        return APIResponse(
            success=True, engine="奇門遁甲",
            data={
                "time": f"{info.year}/{info.month}/{info.day} {info.hour}:00",
                "jieqi": pan.jieqi, "yuan": pan.yuan,
                "dun": "陽遁" if pan.is_yang else "陰遁", "ju": pan.ju_num,
                "zhifu": {"xing": pan.zhifu_xing, "gong": pan.gongs.get(pan.zhifu_gong, pan.gongs[1]).gong_name},
                "zhishi": {"men": pan.zhishi_men},
                "geju": geju,
                "gongs": gongs,
            },
            source_tag="📜《奇門遁甲秘笈》",
        )
    except Exception as e:
        raise HTTPException(400, str(e))

# 康熙筆畫
@app.get("/api/v1/kangxi/{char}")
async def query_kangxi(char: str):
    strokes = get_kangxi_strokes(char)
    if strokes is None:
        raise HTTPException(404, f"未收錄: {char}")
    return {"character": char, "strokes": strokes}

# 統合報告
@app.post("/api/v1/report")
async def generate_report(info: BirthInfo):
    try:
        bazi = get_bazi(info.year, info.month, info.day, info.hour)
        lunar = bazi["lunar"]
        hour_zhi = DIZHI[((info.hour + 1) // 2) % 12]
        
        chart = create_ziwei_chart(lunar.year_gan, lunar.year_zhi, lunar.month, lunar.day, hour_zhi, info.gender)
        pan = create_qimen_pan(info.year, info.month, info.day, info.hour, lunar.day_gan)
        
        results = {
            "bazi": {"pillars": bazi["bazi_str"], "shengxiao": bazi["shengxiao"]},
            "ziwei": {"ju_shu": chart.ju_shu, "ming_stars": chart.gongs[chart.ming_gong_idx].main_stars},
            "qimen": {"ju": f"{'陽' if pan.is_yang else '陰'}遁{pan.ju_num}局", "zhifu": pan.zhifu_xing},
        }
        
        if info.name:
            strokes = get_name_strokes(info.name)
            results["name"] = {"total": sum(strokes.values()), "strokes": strokes}
        
        return APIResponse(
            success=True, engine="統合報告",
            data={"birth": f"{info.year}/{info.month}/{info.day} {info.hour}:00", "lunar": str(lunar), "results": results},
            source_tag="📐古今融合·四術交叉",
        )
    except Exception as e:
        raise HTTPException(400, str(e))

# 靜態檔案
app.mount("/static", StaticFiles(directory="frontend"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
