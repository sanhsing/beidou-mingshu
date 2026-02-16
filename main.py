#!/usr/bin/env python3
"""
北斗命數 Web API v2.3 (完整報告版)
===================================
v2.3 新增：農曆/西曆選擇、完整命理報告

📚 認識論聲明：
術數是個人化決策框架生成器，與天氣預報同構
— 提供機率性參考，不做命定式裁決

建立者：北斗 × 織明
日期：2026-02-07
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import sqlite3
import os

# ===== 引入引擎 =====
from lunar_calendar_v2 import solar_to_lunar, get_bazi, get_hour_ganzhi, LunarDate
from ziwei_engine_v1 import create_ziwei_chart
from qimen_engine_v1 import create_qimen_pan, analyze_geju as analyze_qimen_geju
from name_engine import calculate_wuge
from wuxing_core import GAN, ZHI, GAN_WX, GAN_YY, ten_god, ten_god_field, wx_relation_field, WX_FIELD
from field_translation import (
    get_shishen_translation, get_bagua_translation, get_ziwei_star_translation,
    get_geju_translation, get_shuli_translation, stroke_to_wuxing,
    translate_ziwei_stars, generate_field_analysis, FRAMEWORK_INFO,
    BAGUA_TRANSLATION, ZIWEI_STAR_TRANSLATION, GEJU_TRANSLATION
)
from report_generator import FullReportGenerator, BirthData

# 天干地支定義
TIANGAN = GAN
DIZHI = ZHI

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
    description="古法是根，場論是枝，用戶是花 | v2.3 完整報告版",
    version="2.2.0",
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
    is_lunar: bool = Field(False, description="是否為農曆輸入")
    leap_month: bool = Field(False, description="是否為閏月（僅農曆有效）")

class NameQuery(BaseModel):
    surname: str = Field(..., min_length=1, max_length=2)
    given_name: str = Field(..., min_length=1, max_length=3)

class MeihuaQuery(BaseModel):
    upper_num: int = Field(..., ge=1)
    lower_num: int = Field(..., ge=1)
    dong_yao: int = Field(..., ge=1, le=6)
    question: Optional[str] = None

class FullReportQuery(BaseModel):
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int = Field(12, ge=0, le=23)
    gender: str = Field("男")
    name: Optional[str] = None
    is_lunar: bool = Field(False, description="是否為農曆輸入")
    leap_month: bool = Field(False, description="是否為閏月")
    include_meihua: bool = Field(False, description="是否包含梅花易數")
    meihua_upper: Optional[int] = None
    meihua_lower: Optional[int] = None
    meihua_dong: Optional[int] = None

class APIResponse(BaseModel):
    success: bool
    engine: str
    version: str = "2.1"
    data: Dict[str, Any]
    field_analysis: Optional[Dict[str, Any]] = None
    source_tag: str
    disclaimer: str = "術數為決策參考框架，非命定裁決。趨吉避凶——趨和避都是動詞，主語是人。"

# ===== 農曆轉西曆輔助函數 =====

def full_bazi_analysis(day_master: str, pillars: dict, year_gan: str) -> dict:
    """完整八字分析（含五行強弱、格局、神煞）"""
    try:
        from wuxing_analyzer import analyze_wuxing_strength
        from geju_analyzer import analyze_geju
        from shensha_translation import find_shensha
        
        strength = analyze_wuxing_strength(day_master, pillars)
        geju = analyze_geju(day_master, pillars)
        shensha = find_shensha(day_master, pillars)
        
        return {
            "strength": strength,
            "geju": geju,
            "shensha": shensha,
        }
    except Exception as e:
        return {"error": str(e)}

def full_ziwei_analysis(chart_data: dict) -> dict:
    """完整紫微分析（含四化、輔星）"""
    try:
        from sihua_translation import translate_sihua
        from fuzhu_star_translation import translate_fuzhu_stars, analyze_fuzhu_balance
        
        # 從命宮取得資料
        ming_gong = chart_data.get("gongs", [{}])[chart_data.get("ming_gong_idx", 0)] if chart_data.get("gongs") else {}
        fuzhu_stars = ming_gong.get("auxiliary_stars", []) if isinstance(ming_gong, dict) else []
        
        sihua = chart_data.get("sihua", {})
        
        return {
            "sihua": sihua,
            "fuzhu_analysis": analyze_fuzhu_balance(fuzhu_stars) if fuzhu_stars else {},
        }
    except Exception as e:
        return {"error": str(e)}

def lunar_to_solar(year: int, month: int, day: int, leap: bool = False):
    """
    農曆轉西曆（簡化版）
    基於萬年曆查表法
    """
    # 農曆月份天數資料
    LUNAR_INFO = [
        0x04bd8, 0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950, 0x16554, 0x056a0, 0x09ad0, 0x055d2,
        0x04ae0, 0x0a5b6, 0x0a4d0, 0x0d250, 0x1d255, 0x0b540, 0x0d6a0, 0x0ada2, 0x095b0, 0x14977,
        0x04970, 0x0a4b0, 0x0b4b5, 0x06a50, 0x06d40, 0x1ab54, 0x02b60, 0x09570, 0x052f2, 0x04970,
        0x06566, 0x0d4a0, 0x0ea50, 0x06e95, 0x05ad0, 0x02b60, 0x186e3, 0x092e0, 0x1c8d7, 0x0c950,
        0x0d4a0, 0x1d8a6, 0x0b550, 0x056a0, 0x1a5b4, 0x025d0, 0x092d0, 0x0d2b2, 0x0a950, 0x0b557,
        0x06ca0, 0x0b550, 0x15355, 0x04da0, 0x0a5b0, 0x14573, 0x052b0, 0x0a9a8, 0x0e950, 0x06aa0,
        0x0aea6, 0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260, 0x0f263, 0x0d950, 0x05b57, 0x056a0,
        0x096d0, 0x04dd5, 0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250, 0x0d558, 0x0b540, 0x0b6a0, 0x195a6,
        0x095b0, 0x049b0, 0x0a974, 0x0a4b0, 0x0b27a, 0x06a50, 0x06d40, 0x0af46, 0x0ab60, 0x09570,
        0x04af5, 0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58, 0x055c0, 0x0ab60, 0x096d5, 0x092e0,
        0x0c960, 0x0d954, 0x0d4a0, 0x0da50, 0x07552, 0x056a0, 0x0abb7, 0x025d0, 0x092d0, 0x0cab5,
        0x0a950, 0x0b4a0, 0x0baa4, 0x0ad50, 0x055d9, 0x04ba0, 0x0a5b0, 0x15176, 0x052b0, 0x0a930,
        0x07954, 0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6, 0x0a4e0, 0x0d260, 0x0ea65, 0x0d530,
        0x05aa0, 0x076a3, 0x096d0, 0x04afb, 0x04ad0, 0x0a4d0, 0x1d0b6, 0x0d250, 0x0d520, 0x0dd45,
        0x0b5a0, 0x056d0, 0x055b2, 0x049b0, 0x0a577, 0x0a4b0, 0x0aa50, 0x1b255, 0x06d20, 0x0ada0,
        0x14b63,
    ]
    
    def get_lunar_leap_month(year):
        """取得農曆閏月"""
        info = LUNAR_INFO[year - 1900]
        return info & 0xf
    
    def get_lunar_month_days(year, month, is_leap=False):
        """取得農曆月份天數"""
        info = LUNAR_INFO[year - 1900]
        if is_leap:
            return 30 if info & 0x10000 else 29
        else:
            return 30 if info & (0x10000 >> month) else 29
    
    # 計算從農曆1900年1月1日到目標日期的天數
    # 農曆1900年1月1日 = 西曆1900年1月31日
    days = 0
    
    # 累計整年天數
    for y in range(1900, year):
        info = LUNAR_INFO[y - 1900]
        leap_m = info & 0xf
        for m in range(1, 13):
            days += 30 if info & (0x10000 >> m) else 29
        if leap_m:
            days += 30 if info & 0x10000 else 29
    
    # 累計整月天數
    info = LUNAR_INFO[year - 1900]
    leap_m = info & 0xf
    for m in range(1, month):
        days += 30 if info & (0x10000 >> m) else 29
        if m == leap_m and not leap:
            days += 30 if info & 0x10000 else 29
    
    # 加上閏月（如果有且在目標月之前）
    if leap and month == leap_m:
        days += 30 if info & (0x10000 >> month) else 29
    
    # 加上當月天數
    days += day - 1
    
    # 從西曆1900年1月31日開始計算
    from datetime import date, timedelta
    base = date(1900, 1, 31)
    target = base + timedelta(days=days)
    
    return (target.year, target.month, target.day)

# ===== 曆法轉換輔助函數 =====
def convert_to_solar(info: BirthInfo) -> tuple:
    """統一轉換為西曆，返回 (solar_year, solar_month, solar_day, lunar_info)"""
    if info.is_lunar:
        try:
            solar = lunar_to_solar(info.year, info.month, info.day, info.leap_month)
            lunar = solar_to_lunar(solar[0], solar[1], solar[2])
            return solar[0], solar[1], solar[2], {
                "input_type": "農曆",
                "input_date": f"農曆 {info.year}年{'閏' if info.leap_month else ''}{info.month}月{info.day}日",
                "solar": f"{solar[0]}年{solar[1]}月{solar[2]}日",
                "lunar_str": str(lunar),
                "shengxiao": lunar.shengxiao,
            }
        except Exception as e:
            raise HTTPException(400, f"農曆轉換錯誤：{str(e)}")
    else:
        lunar = solar_to_lunar(info.year, info.month, info.day)
        return info.year, info.month, info.day, {
            "input_type": "西曆",
            "input_date": f"西曆 {info.year}年{info.month}月{info.day}日",
            "solar": f"{info.year}年{info.month}月{info.day}日",
            "lunar_str": str(lunar),
            "shengxiao": lunar.shengxiao,
        }

# ===== 路由 =====
@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.1", "timestamp": datetime.now().isoformat()}

@app.get("/api/info")
async def api_info():
    return {
        "name": "北斗命數 API",
        "version": "2.2.0",
        "framework_version": FRAMEWORK_INFO["version"],
        "engines": ["八字", "紫微斗數", "姓名學", "梅花易數", "奇門遁甲"],
        "features": [
            "場論詮釋", "白話翻譯", "農曆/西曆選擇", "完整報告生成",
            "五行強弱分析", "格局智能判斷", "四化詳解", "神煞白話", "輔星白話"
        ],
        "completed_modules": FRAMEWORK_INFO["completed_modules"],
        "philosophy": FRAMEWORK_INFO.get("philosophy", "古法是根，場論是枝，用戶是花"),
    }

# ===== 場論查詢 API =====
@app.get("/api/v2/field/shishen/{name}")
async def query_shishen(name: str):
    result = get_shishen_translation(name)
    if not result:
        raise HTTPException(404, f"未找到十神：{name}")
    return {"success": True, "shishen": name, **result}

@app.get("/api/v2/field/bagua/{name}")
async def query_bagua(name: str):
    result = get_bagua_translation(name)
    if not result:
        raise HTTPException(404, f"未找到卦象：{name}")
    return {"success": True, **result}

@app.get("/api/v2/field/star/{name}")
async def query_ziwei_star(name: str):
    result = get_ziwei_star_translation(name)
    if not result:
        raise HTTPException(404, f"未找到星曜：{name}")
    return {"success": True, "star": name, **result}

@app.get("/api/v2/field/geju/{name}")
async def query_geju(name: str):
    result = get_geju_translation(name)
    if not result:
        raise HTTPException(404, f"未找到格局：{name}")
    return {"success": True, **result}

@app.get("/api/v2/field/shuli/{num}")
async def query_shuli(num: int):
    result = get_shuli_translation(num)
    return {"success": True, "number": num, **result}

@app.get("/api/v2/field/all")
async def query_all_field():
    return {
        "success": True,
        "bagua": BAGUA_TRANSLATION,
        "ziwei_stars": ZIWEI_STAR_TRANSLATION,
        "geju": GEJU_TRANSLATION,
        "framework": FRAMEWORK_INFO,
    }

# ===== 農曆轉換 =====
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

# ===== 八字分析 =====
@app.post("/api/v1/bazi")
async def analyze_bazi_api(info: BirthInfo):
    try:
        solar_year, solar_month, solar_day, lunar_info = convert_to_solar(info)
        bazi = get_bazi(solar_year, solar_month, solar_day, info.hour)
        lunar = bazi["lunar"]
        day_master = lunar.day_gan
        
        shishen_analysis = []
        for pillar_name, pillar in [("年", bazi["year"]), ("月", bazi["month"]), ("時", bazi["hour"])]:
            gan = pillar[0]
            god_info = ten_god_field(day_master, gan)
            shishen_analysis.append({"pillar": pillar_name, "gan": gan, **god_info})
        
        data = {
            "calendar_info": lunar_info,
            "bazi": bazi["bazi_str"],
            "pillars": {"year": bazi["year"], "month": bazi["month"], "day": bazi["day"], "hour": bazi["hour"]},
            "day_master": day_master,
            "day_element": GAN_WX.get(day_master, ""),
            "shishen_analysis": shishen_analysis,
        }
        
        wx_info = WX_FIELD.get(GAN_WX[day_master], {})
        field_analysis = {
            "core_field": f"{day_master}（{GAN_WX[day_master]}）日主場",
            "field_summary": f"你的核心能量是{GAN_WX[day_master]}，{wx_info.get('場態', '')}",
            "traits": wx_info.get('特徵', ''),
            "modern": wx_info.get('現代', ''),
        }
        
        return APIResponse(
            success=True, engine="八字命理",
            data=data,
            field_analysis=field_analysis,
            source_tag="📜《三命通會》《滴天髓》+ 場論詮釋",
        )
    except Exception as e:
        raise HTTPException(400, str(e))

# ===== 紫微斗數 =====
@app.post("/api/v1/ziwei")
async def analyze_ziwei_api(info: BirthInfo):
    try:
        solar_year, solar_month, solar_day, lunar_info = convert_to_solar(info)
        lunar = solar_to_lunar(solar_year, solar_month, solar_day)
        hour_zhi = DIZHI[((info.hour + 1) // 2) % 12]
        
        chart = create_ziwei_chart(lunar.year_gan, lunar.year_zhi, lunar.month, lunar.day, hour_zhi, info.gender)
        
        gongs = {}
        for g in chart.gongs:
            gongs[g.name] = {"zhi": g.zhi, "main_stars": g.main_stars, "lucky_stars": g.lucky_stars, "sihua": g.sihua}
        
        ming_stars = chart.gongs[chart.ming_gong_idx].main_stars
        star_analysis = translate_ziwei_stars(ming_stars)
        
        data = {
            "calendar_info": lunar_info,
            "ju_shu": chart.ju_shu,
            "ming_gong": chart.gongs[chart.ming_gong_idx].name,
            "ming_stars": ming_stars,
            "shen_gong": chart.gongs[chart.shen_gong_idx].name,
            "shen_stars": chart.gongs[chart.shen_gong_idx].main_stars,
            "sihua": chart.sihua_stars,
            "gongs": gongs,
            "star_analysis": star_analysis,
        }
        
        field_analysis = generate_field_analysis("紫微斗數", {"ming_stars": ming_stars})
        
        return APIResponse(
            success=True, engine="紫微斗數",
            data=data,
            field_analysis=field_analysis,
            source_tag="📜《紫微斗數全書》+ 場論詮釋",
        )
    except Exception as e:
        raise HTTPException(400, str(e))

# ===== 姓名學 =====
@app.post("/api/v1/name")
async def analyze_name_api(query: NameQuery):
    try:
        full_name = query.surname + query.given_name
        strokes = get_name_strokes(full_name)
        
        result = calculate_wuge(query.surname, list(query.given_name), strokes)
        
        wuge_analysis = {
            "tian": {"value": result.tian, "wuxing": stroke_to_wuxing(result.tian), "shuli": get_shuli_translation(result.tian)},
            "ren": {"value": result.ren, "wuxing": stroke_to_wuxing(result.ren), "shuli": get_shuli_translation(result.ren)},
            "di": {"value": result.di, "wuxing": stroke_to_wuxing(result.di), "shuli": get_shuli_translation(result.di)},
            "wai": {"value": result.wai, "wuxing": stroke_to_wuxing(result.wai), "shuli": get_shuli_translation(result.wai)},
            "zong": {"value": result.zong, "wuxing": stroke_to_wuxing(result.zong), "shuli": get_shuli_translation(result.zong)},
        }
        
        data = {
            "name": full_name,
            "strokes": strokes,
            "total": sum(strokes.values()),
            "wuge": {"tian": result.tian, "ren": result.ren, "di": result.di, "wai": result.wai, "zong": result.zong},
            "sancai": result.sancai_str,
            "wuge_analysis": wuge_analysis,
        }
        
        ren_shuli = get_shuli_translation(result.ren)
        field_analysis = {
            "core_field": "人格場（最重要）",
            "field_summary": f"人格{result.ren}，{ren_shuli['name']}（{ren_shuli['type']}）— {ren_shuli['meaning']}",
            "sancai_field": f"三才{result.sancai_str}：{stroke_to_wuxing(result.tian)}→{stroke_to_wuxing(result.ren)}→{stroke_to_wuxing(result.di)}",
        }
        
        return APIResponse(
            success=True, engine="姓名學",
            data=data,
            field_analysis=field_analysis,
            source_tag="📐《康熙字典》+ 熊崎氏 + 場論詮釋",
        )
    except Exception as e:
        raise HTTPException(400, str(e))

# ===== 梅花易數 =====
@app.post("/api/v1/meihua")
async def analyze_meihua_api(query: MeihuaQuery):
    try:
        BAGUA_NAMES = ["乾", "兌", "離", "震", "巽", "坎", "艮", "坤"]
        upper = BAGUA_NAMES[(query.upper_num - 1) % 8]
        lower = BAGUA_NAMES[(query.lower_num - 1) % 8]
        
        upper_info = get_bagua_translation(upper)
        lower_info = get_bagua_translation(lower)
        
        data = {
            "upper_gua": upper,
            "lower_gua": lower,
            "dong_yao": query.dong_yao,
            "question": query.question,
            "upper_analysis": upper_info,
            "lower_analysis": lower_info,
        }
        
        field_analysis = {
            "upper_field": f"上卦{upper}：{upper_info.get('vernacular', '')} — {upper_info.get('field', '')}",
            "lower_field": f"下卦{lower}：{lower_info.get('vernacular', '')} — {lower_info.get('field', '')}",
            "scenario": f"上卦適用：{upper_info.get('scenario', '')}",
        }
        
        return APIResponse(
            success=True, engine="梅花易數",
            data=data,
            field_analysis=field_analysis,
            source_tag="📜《梅花易數》+ 場論詮釋",
        )
    except Exception as e:
        raise HTTPException(400, str(e))

# ===== 奇門遁甲 =====
@app.post("/api/v1/qimen")
async def analyze_qimen_api(info: BirthInfo):
    try:
        solar_year, solar_month, solar_day, lunar_info = convert_to_solar(info)
        lunar = solar_to_lunar(solar_year, solar_month, solar_day)
        pan = create_qimen_pan(solar_year, solar_month, solar_day, info.hour, lunar.day_gan)
        geju = analyze_geju(pan)
        
        gongs = {}
        for num, g in pan.gongs.items():
            gongs[g.gong_name] = {"direction": g.direction, "dipan": g.dipan_gan, "tianpan": g.tianpan_gan, "men": g.men, "xing": g.xing, "shen": g.shen}
        
        return APIResponse(
            success=True, engine="奇門遁甲",
            data={
                "calendar_info": lunar_info,
                "jieqi": pan.jieqi, "yuan": pan.yuan,
                "dun": "陽遁" if pan.is_yang else "陰遁", "ju": pan.ju_num,
                "zhifu": {"xing": pan.zhifu_xing, "gong": pan.gongs.get(pan.zhifu_gong, pan.gongs[1]).gong_name},
                "zhishi": {"men": pan.zhishi_men},
                "geju": geju,
                "gongs": gongs,
            },
            source_tag="📜《奇門遁甲秘笈》+ 場論詮釋",
        )
    except Exception as e:
        raise HTTPException(400, str(e))

# ===== 康熙筆畫 =====
@app.get("/api/v1/kangxi/{char}")
async def query_kangxi(char: str):
    strokes = get_kangxi_strokes(char)
    if strokes is None:
        raise HTTPException(404, f"未收錄: {char}")
    return {"character": char, "strokes": strokes, "wuxing": stroke_to_wuxing(strokes)}

# ===== 完整報告生成 =====
@app.post("/api/v2/full-report")
async def generate_full_report_api(query: FullReportQuery):
    """生成完整命理分析報告"""
    try:
        info = BirthInfo(
            year=query.year, month=query.month, day=query.day, hour=query.hour,
            gender=query.gender, name=query.name,
            is_lunar=query.is_lunar, leap_month=query.leap_month,
        )
        
        solar_year, solar_month, solar_day, lunar_info = convert_to_solar(info)
        
        # 八字分析
        bazi = get_bazi(solar_year, solar_month, solar_day, query.hour)
        lunar = bazi["lunar"]
        day_master = lunar.day_gan
        
        shishen_analysis = []
        for pillar_name, pillar in [("年", bazi["year"]), ("月", bazi["month"]), ("時", bazi["hour"])]:
            gan = pillar[0]
            god_info = ten_god_field(day_master, gan)
            shishen_analysis.append({"pillar": pillar_name, "gan": gan, **god_info})
        
        bazi_data = {
            "pillars": {"year": bazi["year"], "month": bazi["month"], "day": bazi["day"], "hour": bazi["hour"]},
            "day_master": day_master,
            "day_element": GAN_WX.get(day_master, ""),
            "shishen_analysis": shishen_analysis,
            "wuxing_count": {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0},
        }
        
        # 紫微分析
        hour_zhi = DIZHI[((query.hour + 1) // 2) % 12]
        chart = create_ziwei_chart(lunar.year_gan, lunar.year_zhi, lunar.month, lunar.day, hour_zhi, query.gender)
        
        gongs = {}
        for g in chart.gongs:
            gongs[g.name] = {"zhi": g.zhi, "main_stars": g.main_stars, "lucky_stars": g.lucky_stars, "sihua": g.sihua}
        
        ziwei_data = {
            "ju_shu": chart.ju_shu,
            "ming_gong": chart.gongs[chart.ming_gong_idx].name,
            "ming_stars": chart.gongs[chart.ming_gong_idx].main_stars,
            "shen_gong": chart.gongs[chart.shen_gong_idx].name,
            "shen_stars": chart.gongs[chart.shen_gong_idx].main_stars,
            "sihua": chart.sihua_stars,
            "gongs": gongs,
        }
        
        # 姓名分析
        name_data = None
        if query.name and len(query.name) >= 2:
            strokes = get_name_strokes(query.name)
            surname = query.name[0]
            given = query.name[1:]
            result = calculate_wuge(surname, list(given), strokes)
            
            name_data = {
                "name": query.name,
                "strokes": strokes,
                "wuge": {"tian": result.tian, "ren": result.ren, "di": result.di, "wai": result.wai, "zong": result.zong},
                "wuge_analysis": {
                    "tian": {"value": result.tian, "wuxing": stroke_to_wuxing(result.tian), "shuli": get_shuli_translation(result.tian)},
                    "ren": {"value": result.ren, "wuxing": stroke_to_wuxing(result.ren), "shuli": get_shuli_translation(result.ren)},
                    "di": {"value": result.di, "wuxing": stroke_to_wuxing(result.di), "shuli": get_shuli_translation(result.di)},
                    "wai": {"value": result.wai, "wuxing": stroke_to_wuxing(result.wai), "shuli": get_shuli_translation(result.wai)},
                    "zong": {"value": result.zong, "wuxing": stroke_to_wuxing(result.zong), "shuli": get_shuli_translation(result.zong)},
                },
                "sancai": result.sancai_str,
            }
        
        # 梅花分析
        meihua_data = None
        if query.include_meihua and query.meihua_upper and query.meihua_lower and query.meihua_dong:
            BAGUA_NAMES = ["乾", "兌", "離", "震", "巽", "坎", "艮", "坤"]
            upper = BAGUA_NAMES[(query.meihua_upper - 1) % 8]
            lower = BAGUA_NAMES[(query.meihua_lower - 1) % 8]
            meihua_data = {"upper_gua": upper, "lower_gua": lower, "dong_yao": query.meihua_dong}
        
        # 生成報告（使用 v2 報告生成器）
        birth_data = BirthData(
            year=query.year, month=query.month, day=query.day, hour=query.hour,
            gender=query.gender, name=query.name, is_lunar=query.is_lunar,
        )
        
        # 取得四柱
        pillars = {"year": bazi["year"], "month": bazi["month"], "day": bazi["day"], "hour": bazi["hour"]}
        year_gan = bazi["year"][0]
        
        # v2.0 增強：完整八字分析（含五行強弱、格局、神煞）
        bazi_analysis = full_bazi_analysis(day_master, pillars, year_gan)
        
        # 建立紫微 chart_data
        chart_data = {
            "ju_shu": chart.ju_shu,
            "ming_gong": chart.gongs[chart.ming_gong_idx].name,
            "ming_gong_idx": chart.ming_gong_idx,
            "shen_gong": chart.gongs[chart.shen_gong_idx].name,
            "shen_gong_idx": chart.shen_gong_idx,
            "sihua": chart.sihua_stars,
            "gongs": gongs,
        }
        
        # v2.0 增強：完整紫微分析（含輔星）
        ziwei_analysis = full_ziwei_analysis(chart_data)
        
        # 生成 v2.0 報告
        generator = FullReportGenerator()
        report_text = generator.generate_full_report(
            birth=birth_data,
            lunar_info=lunar_info,
            bazi=bazi_analysis,
            ziwei=ziwei_analysis,
            name_data=name_data,
            meihua=meihua_data,
            year_gan=lunar_info.get('year_gan', ''),
        )
        
        return {
            "success": True, "engine": "完整報告", "version": "2.2",
            "report_text": report_text,
            "data": {
                "calendar_info": lunar_info,
                "bazi": bazi_analysis,
                "ziwei": ziwei_analysis,
                "name": name_data,
                "meihua": meihua_data
            },
            "source_tag": "📐古今融合·四術交叉·場論詮釋 v2.0",
        }
    except Exception as e:
        raise HTTPException(400, str(e))

# ===== 純文字報告 =====
@app.post("/api/v2/full-report/text", response_class=PlainTextResponse)
async def generate_full_report_text(query: FullReportQuery):
    result = await generate_full_report_api(query)
    return result["report_text"]

# ===== 統合報告（舊版相容）=====
@app.post("/api/v1/report")
async def generate_report(info: BirthInfo):
    try:
        solar_year, solar_month, solar_day, lunar_info = convert_to_solar(info)
        bazi = get_bazi(solar_year, solar_month, solar_day, info.hour)
        lunar = bazi["lunar"]
        hour_zhi = DIZHI[((info.hour + 1) // 2) % 12]
        day_master = lunar.day_gan
        
        chart = create_ziwei_chart(lunar.year_gan, lunar.year_zhi, lunar.month, lunar.day, hour_zhi, info.gender)
        pan = create_qimen_pan(solar_year, solar_month, solar_day, info.hour, lunar.day_gan)
        
        ming_stars = chart.gongs[chart.ming_gong_idx].main_stars
        star_analysis = translate_ziwei_stars(ming_stars)
        
        results = {
            "bazi": {"pillars": bazi["bazi_str"], "shengxiao": bazi["shengxiao"], "day_master": day_master, "day_element": GAN_WX[day_master]},
            "ziwei": {"ju_shu": chart.ju_shu, "ming_stars": ming_stars, "star_analysis": star_analysis},
            "qimen": {"ju": f"{'陽' if pan.is_yang else '陰'}遁{pan.ju_num}局", "zhifu": pan.zhifu_xing},
        }
        
        if info.name and len(info.name) > 1:
            strokes = get_name_strokes(info.name)
            name_result = calculate_wuge(info.name[0], list(info.name[1:]), strokes)
            ren_shuli = get_shuli_translation(name_result.ren)
            results["name"] = {"total": sum(strokes.values()), "strokes": strokes, "ren_ge": name_result.ren, "ren_analysis": ren_shuli}
        
        field_analysis = {"core_summary": f"日主{day_master}（{GAN_WX[day_master]}），命宮主星{ming_stars[0] if ming_stars else '無'}", "suggestions": []}
        if star_analysis:
            main_star = star_analysis[0]
            field_analysis["suggestions"].append(f"命宮{main_star.get('star', '')}：{main_star.get('vernacular', '')}")
            field_analysis["suggestions"].append(f"適合職業：{main_star.get('career', '')}")
        
        return APIResponse(
            success=True, engine="統合報告",
            data={"calendar_info": lunar_info, "results": results},
            field_analysis=field_analysis,
            source_tag="📐古今融合·四術交叉·場論詮釋",
        )
    except Exception as e:
        raise HTTPException(400, str(e))

# ===== 靜態檔案 =====
app.mount("/static", StaticFiles(directory="frontend"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
