#!/usr/bin/env python3
"""
北斗命數 Web API v2.4 (完整版)
==============================
XTF任務：融-F1 | @11star 協作
方法論：XTF8 確定度標註 + XTFS 四塔驗證

v2.4 新增：
- B: 紫微流年四化飛星
- C: JWT 用戶認證
- D: 命盤比對（合婚/親子/合作）
- E: OpenAPI 文檔

📚 認識論聲明：
術數是個人化決策框架生成器，與天氣預報同構
— 提供機率性參考，不做命定式裁決

建立者：北斗 × 織明
日期：2026-02-07
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

# ===== v2.4 新增模組 =====
# B: 紫微流年
from ziwei_liunian import analyze_ziwei_liunian, generate_ziwei_liunian_report

# C: 認證系統
from auth_jwt import AuthManager, get_auth_manager, User

# D: 命盤比對
from chart_matching import match_charts, generate_match_report

# E: API 文檔
from api_docs import generate_openapi_spec, API_ENDPOINTS

# 大運流年
from dayun_calculator import calculate_dayun, get_current_dayun
from liunian_analyzer import analyze_liunian, analyze_liunian_range
from daxian_calculator import calculate_daxian, get_current_daxian

# 天干地支定義
TIANGAN = GAN
DIZHI = ZHI

# ===== FastAPI App =====
app = FastAPI(
    title="北斗命數 API",
    description="""
北斗命數命理分析系統 API v2.4

## 功能模組
- 🔮 八字分析：四柱八字、大運流年
- ⭐ 紫微斗數：命盤排盤、大限流年、四化飛星
- 📝 姓名學：五格分析、三才配置
- 🌸 梅花易數：起卦解卦
- 💑 命盤比對：合婚、親子、合作

## XTF8 確定度標註
- ★★★★★ 計算公式（可驗證）
- ★★★☆☆ 經驗統計（參考性質）
- ★★☆☆☆ 推測建議（僅供參考）

古法是根，場論是枝，用戶是花
""",
    version="2.4.0",
    contact={"name": "北斗", "email": "beidou@example.com"},
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== 資料模型 =====
class BirthInfo(BaseModel):
    year: int = Field(..., ge=1900, le=2100, description="出生年")
    month: int = Field(..., ge=1, le=12, description="出生月")
    day: int = Field(..., ge=1, le=31, description="出生日")
    hour: int = Field(12, ge=0, le=23, description="出生時（0-23）")
    gender: str = Field("男", description="性別")
    name: Optional[str] = Field(None, description="姓名")
    is_lunar: bool = Field(False, description="是否農曆")


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="用戶名")
    password: str = Field(..., min_length=6, description="密碼")
    email: Optional[str] = Field(None, description="電子郵件")


class LoginRequest(BaseModel):
    username: str = Field(..., description="用戶名")
    password: str = Field(..., description="密碼")


class MatchRequest(BaseModel):
    person1: Dict = Field(..., description="甲方資料")
    person2: Dict = Field(..., description="乙方資料")
    match_type: str = Field("marriage", description="比對類型：marriage/parent_child/cooperation")


class ZiweiLiunianRequest(BaseModel):
    year: int = Field(..., description="分析年份")
    ming_gong_zhi: str = Field(..., description="命宮地支")
    gongs: Optional[List[Dict]] = Field(None, description="十二宮資料")


class DayunRequest(BaseModel):
    year_gan: str = Field(..., description="年干")
    month_ganzhi: str = Field(..., description="月柱干支")
    gender: str = Field(..., description="性別")
    birth_year: int = Field(..., description="出生年")
    birth_month: int = Field(..., description="出生月")
    birth_day: int = Field(..., description="出生日")


class LiunianRequest(BaseModel):
    day_master: str = Field(..., description="日主天干")
    pillars: Dict = Field(..., description="四柱")
    year: int = Field(..., description="分析年份")
    is_strong: bool = Field(True, description="是否身強")


# ===== 認證依賴 =====
async def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[User]:
    """認證依賴：從 Header 取得用戶"""
    if not authorization:
        return None
    
    if not authorization.startswith("Bearer "):
        return None
    
    token = authorization[7:]
    auth = get_auth_manager()
    valid, user, error = auth.verify(token)
    
    return user if valid else None


async def require_auth(authorization: Optional[str] = Header(None)) -> User:
    """強制認證依賴"""
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="未認證或 Token 無效")
    return user


# ===== 認證 API =====
@app.post("/api/auth/register", tags=["認證"])
async def register(req: RegisterRequest):
    """用戶註冊"""
    auth = get_auth_manager()
    success, msg, user = auth.register(req.username, req.password, req.email or "")
    
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    
    return {"success": True, "message": msg, "user_id": user.user_id}


@app.post("/api/auth/login", tags=["認證"])
async def login(req: LoginRequest):
    """用戶登入"""
    auth = get_auth_manager()
    success, msg, tokens = auth.login(req.username, req.password)
    
    if not success:
        raise HTTPException(status_code=401, detail=msg)
    
    return {"success": True, "message": msg, **tokens}


@app.get("/api/auth/me", tags=["認證"])
async def get_me(user: User = Depends(require_auth)):
    """取得當前用戶資訊"""
    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }


# ===== 八字 API =====
@app.post("/api/bazi/calculate", tags=["八字"])
async def calculate_bazi(info: BirthInfo):
    """八字排盤"""
    try:
        if info.is_lunar:
            lunar = LunarDate(info.year, info.month, info.day, False)
        else:
            lunar = solar_to_lunar(info.year, info.month, info.day)
        
        bazi = get_bazi(lunar.year, lunar.month, lunar.day)
        hour_gz = get_hour_ganzhi(bazi["day"][0], info.hour)
        
        day_master = bazi["day"][0]
        day_master_wx = GAN_WX.get(day_master, "")
        
        # 計算五行統計
        all_chars = [bazi["year"][0], bazi["year"][1], bazi["month"][0], bazi["month"][1],
                     bazi["day"][0], bazi["day"][1], hour_gz[0], hour_gz[1]]
        wx_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        for c in all_chars:
            wx = GAN_WX.get(c) or {"子": "水", "丑": "土", "寅": "木", "卯": "木",
                                   "辰": "土", "巳": "火", "午": "火", "未": "土",
                                   "申": "金", "酉": "金", "戌": "土", "亥": "水"}.get(c, "")
            if wx:
                wx_count[wx] += 1
        
        return {
            "year": "".join(bazi["year"]),
            "month": "".join(bazi["month"]),
            "day": "".join(bazi["day"]),
            "hour": "".join(hour_gz),
            "day_master": day_master,
            "day_master_wx": day_master_wx,
            "wuxing_count": wx_count,
            "lunar_info": {
                "year": lunar.year,
                "month": lunar.month,
                "day": lunar.day,
            },
            "certainty": "★★★★★",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/bazi/dayun", tags=["八字"])
async def api_calculate_dayun(req: DayunRequest):
    """八字大運計算"""
    try:
        result = calculate_dayun(
            req.year_gan, req.month_ganzhi, req.gender,
            req.birth_year, req.birth_month, req.birth_day
        )
        current = get_current_dayun(result, datetime.now().year)
        
        return {
            "direction": result["direction"],
            "qiyun_age": result["qiyun_age"],
            "qiyun_year": result["qiyun_year"],
            "dayun_list": result["dayun_list"],
            "current_dayun": current,
            "certainty": "★★★★★",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/bazi/liunian", tags=["八字"])
async def api_analyze_liunian(req: LiunianRequest):
    """八字流年分析"""
    try:
        result = analyze_liunian(req.day_master, req.pillars, req.year, req.is_strong)
        return {
            **result,
            "certainty": "★★★☆☆",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== 紫微 API =====
@app.post("/api/ziwei/calculate", tags=["紫微"])
async def calculate_ziwei(info: BirthInfo):
    """紫微排盤"""
    try:
        if info.is_lunar:
            lunar = LunarDate(info.year, info.month, info.day, False)
        else:
            lunar = solar_to_lunar(info.year, info.month, info.day)
        
        chart = create_ziwei_chart(lunar.year, lunar.month, lunar.day, info.hour, info.gender)
        
        return {
            "ju_shu": chart.get("ju_shu", ""),
            "ming_gong": chart.get("ming_gong", ""),
            "ming_gong_idx": chart.get("ming_gong_idx", 0),
            "shen_gong": chart.get("shen_gong", ""),
            "ming_stars": chart.get("ming_stars", []),
            "sihua": chart.get("sihua", {}),
            "gongs": chart.get("gongs", []),
            "certainty": "★★★★★",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ziwei/liunian", tags=["紫微"])
async def api_ziwei_liunian(req: ZiweiLiunianRequest):
    """紫微流年四化分析"""
    try:
        result = analyze_ziwei_liunian(req.year, req.ming_gong_zhi, req.gongs)
        return {
            **result,
            "certainty": "★★★☆☆",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ziwei/daxian", tags=["紫微"])
async def api_calculate_daxian(
    year_gan: str,
    gender: str,
    ju_shu: str,
    ming_gong_idx: int,
    birth_year: int,
):
    """紫微大限計算"""
    try:
        result = calculate_daxian(year_gan, gender, ju_shu, ming_gong_idx, birth_year)
        current = get_current_daxian(result, datetime.now().year)
        
        return {
            "direction": result["direction"],
            "start_age": result["start_age"],
            "daxian_list": result["daxian_list"],
            "current_daxian": current,
            "certainty": "★★★★★",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== 比對 API =====
@app.post("/api/match", tags=["比對"])
async def api_match_charts(req: MatchRequest):
    """命盤比對"""
    try:
        result = match_charts(req.person1, req.person2, req.match_type)
        return {
            **result,
            "certainty": "★★★☆☆",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/match/report", tags=["比對"])
async def api_match_report(req: MatchRequest):
    """命盤比對報告"""
    try:
        result = match_charts(req.person1, req.person2, req.match_type)
        report = generate_match_report(result)
        return {
            "result": result,
            "report": report,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== 姓名 API =====
@app.post("/api/name/analyze", tags=["姓名"])
async def analyze_name(surname: str, given_name: str):
    """姓名五格分析"""
    try:
        result = calculate_wuge(surname, given_name)
        return {
            **result,
            "certainty": "★★★★☆",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== 完整報告 API =====
@app.post("/api/report/full", tags=["報告"])
async def generate_full_report(info: BirthInfo):
    """生成完整命理報告"""
    try:
        # 計算農曆
        if info.is_lunar:
            lunar = LunarDate(info.year, info.month, info.day, False)
        else:
            lunar = solar_to_lunar(info.year, info.month, info.day)
        
        # 八字
        bazi = get_bazi(lunar.year, lunar.month, lunar.day)
        hour_gz = get_hour_ganzhi(bazi["day"][0], info.hour)
        
        bazi_data = {
            "year": "".join(bazi["year"]),
            "month": "".join(bazi["month"]),
            "day": "".join(bazi["day"]),
            "hour": "".join(hour_gz),
            "day_master": bazi["day"][0],
        }
        
        # 紫微
        ziwei = create_ziwei_chart(lunar.year, lunar.month, lunar.day, info.hour, info.gender)
        
        # 生成報告
        gen = FullReportGenerator()
        birth_data = BirthData(
            year=info.year, month=info.month, day=info.day, hour=info.hour,
            gender=info.gender, name=info.name, is_lunar=info.is_lunar
        )
        lunar_info = {"lunar_year": lunar.year, "lunar_month": lunar.month, "lunar_day": lunar.day}
        
        report = gen.generate_full_report(
            birth_data, lunar_info, bazi_data, ziwei,
            year_gan=bazi["year"][0]
        )
        
        return {
            "report": report,
            "bazi": bazi_data,
            "ziwei": {
                "ju_shu": ziwei.get("ju_shu"),
                "ming_gong": ziwei.get("ming_gong"),
                "ming_stars": ziwei.get("ming_stars"),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== 系統 API =====
@app.get("/api/openapi-spec", tags=["系統"])
async def get_openapi():
    """取得 OpenAPI 規範"""
    return generate_openapi_spec()


@app.get("/api/version", tags=["系統"])
async def get_version():
    """取得版本資訊"""
    return {
        "version": "2.4.0",
        "name": "北斗命數 API",
        "features": ["八字", "紫微", "姓名", "梅花", "比對", "認證"],
        "xtf8": "確定度標註系統",
        "build_date": "2026-02-07",
    }


@app.get("/api/endpoints", tags=["系統"])
async def list_endpoints():
    """列出所有端點"""
    return {
        "count": len(API_ENDPOINTS),
        "endpoints": [
            {
                "path": ep.path,
                "method": ep.method.value,
                "summary": ep.summary,
                "tags": ep.tags,
                "requires_auth": ep.requires_auth,
            }
            for ep in API_ENDPOINTS
        ],
    }


# ===== 首頁 =====
@app.get("/", response_class=HTMLResponse, tags=["系統"])
async def root():
    """首頁"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>北斗命數 API v2.4</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        .feature { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
        a { color: #0066cc; }
    </style>
</head>
<body>
    <h1>🌟 北斗命數 API v2.4</h1>
    <p>古法是根，場論是枝，用戶是花</p>
    
    <h2>功能模組</h2>
    <div class="feature">🔮 八字分析：四柱八字、大運流年</div>
    <div class="feature">⭐ 紫微斗數：命盤排盤、大限流年、四化飛星</div>
    <div class="feature">📝 姓名學：五格分析、三才配置</div>
    <div class="feature">💑 命盤比對：合婚、親子、合作</div>
    <div class="feature">🔐 用戶認證：JWT Token</div>
    
    <h2>API 文檔</h2>
    <p><a href="/docs">Swagger UI</a> | <a href="/redoc">ReDoc</a> | <a href="/api/openapi-spec">OpenAPI JSON</a></p>
    
    <h2>XTF8 確定度標註</h2>
    <ul>
        <li>★★★★★ 計算公式（可驗證）</li>
        <li>★★★☆☆ 經驗統計（參考性質）</li>
        <li>★★☆☆☆ 推測建議（僅供參考）</li>
    </ul>
    
    <p><small>建立者：北斗 × 織明 | 2026-02-07</small></p>
</body>
</html>
"""


# ===== 靜態文件 =====
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
