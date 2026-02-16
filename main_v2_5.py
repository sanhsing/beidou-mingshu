#!/usr/bin/env python3
"""
北斗命數 Web API v2.5 (完整版)
==============================
XTF任務：融-F1 | @11star 協作
方法論：XTF8 確定度標註 + XTFS 四塔驗證

v2.5 新增：
- 易經64卦場論翻譯 API
- 易經384爻場論翻譯 API
- 場論翻譯系統 v3.0 整合

📚 認識論聲明：
術數是個人化決策框架生成器，與天氣預報同構
— 提供機率性參考，不做命定式裁決

建立者：北斗 × 織明
日期：2026-02-08
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import sqlite3
import os

# ===== 核心引擎 =====
from lunar_calendar_v2 import solar_to_lunar, get_bazi, get_hour_ganzhi, LunarDate
from ziwei_engine_v1 import create_ziwei_chart
from name_engine import calculate_wuge
from wuxing_core import GAN, ZHI, GAN_WX, GAN_YY, ten_god, ten_god_field, wx_relation_field, WX_FIELD
from field_translation import (
    get_shishen_translation, get_bagua_translation, get_ziwei_star_translation,
    get_geju_translation, get_shuli_translation, stroke_to_wuxing,
    translate_ziwei_stars, generate_field_analysis, FRAMEWORK_INFO,
    BAGUA_TRANSLATION, ZIWEI_STAR_TRANSLATION, GEJU_TRANSLATION
)
from report_generator import FullReportGenerator, BirthData

# ===== v2.4 模組 =====
from ziwei_liunian import analyze_ziwei_liunian, generate_ziwei_liunian_report
from auth_jwt import AuthManager, get_auth_manager, User
from chart_matching import match_charts, generate_match_report
from api_docs import generate_openapi_spec, API_ENDPOINTS
from dayun_calculator import calculate_dayun, get_current_dayun
from liunian_analyzer import analyze_liunian, analyze_liunian_range
from daxian_calculator import calculate_daxian, get_current_daxian

# ===== v2.5 新增：易經模組 =====
from yijing_api import router as yijing_router
from field_translation_v3 import (
    get_translation_status,
    translate_yijing_gua,
    translate_yijing_yao,
    get_full_gua_with_yao
)

# 天干地支定義
TIANGAN = GAN
DIZHI = ZHI

# ===== FastAPI App =====
app = FastAPI(
    title="北斗命數 API",
    description="""
北斗命數命理分析系統 API v2.5

## 功能模組
- 🔮 八字分析：四柱八字、大運流年
- ⭐ 紫微斗數：命盤排盤、大限流年、四化飛星
- 📝 姓名學：五格分析、三才配置
- 🌸 梅花易數：起卦解卦
- 💑 命盤比對：合婚、親子、合作
- ☯️ 易經：64卦場論翻譯、384爻白話詮釋（v2.5新增）

## XTF8 確定度標註
- ★★★★★ 計算公式（可驗證）
- ★★★☆☆ 經驗統計（參考性質）
- ★★☆☆☆ 推測建議（僅供參考）

古法是根，場論是枝，用戶是花
""",
    version="2.5.0",
    contact={"name": "北斗", "email": "beidou@example.com"},
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 註冊路由 =====
app.include_router(yijing_router)

# ===== 根路由 =====
@app.get("/")
async def root():
    """API 根節點"""
    return {
        "name": "北斗命數 API",
        "version": "2.5.0",
        "modules": [
            "八字分析", "紫微斗數", "姓名學", "梅花易數",
            "命盤比對", "易經64卦", "易經384爻"
        ],
        "endpoints": {
            "bazi": "/bazi/full",
            "ziwei": "/ziwei/chart",
            "name": "/name/wuge",
            "meihua": "/meihua/qigua",
            "yijing": "/yijing/gua/{num}"
        }
    }

@app.get("/status")
async def get_status():
    """獲取系統狀態"""
    translation_status = get_translation_status()
    return {
        "api_version": "2.5.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "translation_modules": translation_status["modules"]
    }

# ===== 八字相關路由 =====

class BaziInput(BaseModel):
    year: int = Field(..., description="出生年（西元）")
    month: int = Field(..., ge=1, le=12, description="出生月")
    day: int = Field(..., ge=1, le=31, description="出生日")
    hour: int = Field(..., ge=0, le=23, description="出生時（0-23）")
    gender: str = Field("M", description="性別 M/F")

@app.post("/bazi/full")
async def analyze_bazi_full(data: BaziInput):
    """完整八字分析"""
    try:
        # 計算農曆
        lunar = solar_to_lunar(data.year, data.month, data.day)
        
        # 計算八字
        bazi = get_bazi(data.year, data.month, data.day, data.hour)
        
        # 計算時柱
        hour_gz = get_hour_ganzhi(bazi["day_gan"], data.hour)
        
        # 日主五行
        day_gan = bazi["day_gan"]
        day_wx = GAN_WX[day_gan]
        
        return {
            "input": data.dict(),
            "lunar": {
                "year": lunar.year,
                "month": lunar.month,
                "day": lunar.day,
                "leap": lunar.leap
            },
            "bazi": {
                "year": f"{bazi['year_gan']}{bazi['year_zhi']}",
                "month": f"{bazi['month_gan']}{bazi['month_zhi']}",
                "day": f"{bazi['day_gan']}{bazi['day_zhi']}",
                "hour": f"{hour_gz['gan']}{hour_gz['zhi']}"
            },
            "day_master": {
                "gan": day_gan,
                "wuxing": day_wx,
                "yinyang": GAN_YY[day_gan]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== 紫微相關路由 =====

@app.post("/ziwei/chart")
async def get_ziwei_chart(data: BaziInput):
    """紫微斗數排盤"""
    try:
        chart = create_ziwei_chart(
            data.year, data.month, data.day, data.hour, data.gender
        )
        return chart
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== 姓名學相關路由 =====

class NameInput(BaseModel):
    surname: str = Field(..., description="姓")
    given_name: str = Field(..., description="名")

@app.post("/name/wuge")
async def analyze_name_wuge(data: NameInput):
    """姓名五格分析"""
    try:
        result = calculate_wuge(data.surname, data.given_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== 場論翻譯路由 =====

@app.get("/translate/shishen/{shishen}")
async def translate_shishen(shishen: str):
    """翻譯十神"""
    result = get_shishen_translation(shishen)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/translate/bagua/{gua}")
async def translate_bagua(gua: str):
    """翻譯八卦"""
    result = get_bagua_translation(gua)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/translate/ziwei/{star}")
async def translate_ziwei_star(star: str):
    """翻譯紫微主星"""
    result = get_ziwei_star_translation(star)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

# ===== 運行入口 =====

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
