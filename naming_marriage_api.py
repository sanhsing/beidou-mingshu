#!/usr/bin/env python3
"""
naming_marriage_api.py - 命名 + 婚嫁 API 端點
北斗命數 v3.1.2

功能：
1. 個人命名分析（配合八字）
2. 新生兒命名建議
3. 改名比對
4. 公司行號命名
5. 合婚分析（雙盤匹配）
6. 嫁娶擇日擇時

@織明 × @流祇
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date

# 創建路由
router = APIRouter(prefix="/api/v1/naming", tags=["naming-marriage"])

# 嘗試導入核心模組
try:
    from mingshu_naming_marriage_v1 import NamingMarriageAPI
    naming_api = NamingMarriageAPI()
    MODULES_LOADED = True
except ImportError as e:
    print(f"⚠️ 命名婚嫁模組未載入: {e}")
    MODULES_LOADED = False
    naming_api = None

# ============================================================
# 請求模型
# ============================================================

class BirthInfoModel(BaseModel):
    """出生資訊"""
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int = Field(12, ge=0, le=23)
    gender: str = Field("M", description="M=男, F=女")
    calendar: str = Field("solar", description="solar=國曆, lunar=農曆")
    name: Optional[str] = None

class NameAnalyzeRequest(BaseModel):
    """姓名分析請求"""
    surname: str = Field(..., min_length=1, max_length=2, description="姓氏")
    given_name: str = Field(..., min_length=1, max_length=3, description="名字")
    birth_info: Optional[BirthInfoModel] = None

class BabyNamingRequest(BaseModel):
    """新生兒命名請求"""
    surname: str = Field(..., min_length=1, max_length=2)
    birth_info: BirthInfoModel
    gender: str = Field("M")
    count: int = Field(10, ge=1, le=30)

class RenameCompareRequest(BaseModel):
    """改名比對請求"""
    surname: str
    old_name: str
    new_name: str
    birth_info: Optional[BirthInfoModel] = None

class CompanyNameRequest(BaseModel):
    """公司命名請求"""
    company_name: str = Field(..., min_length=2)
    industry: Optional[str] = Field(None, description="行業: TECH/FINANCE/FOOD/RETAIL/EDUCATION/HEALTH/SERVICE")

class CompanySuggestRequest(BaseModel):
    """公司名建議請求"""
    base_name: str = Field(..., min_length=1, description="基礎字/概念")
    industry: str = Field("TECH")
    count: int = Field(5, ge=1, le=20)

class MarriageMatchRequest(BaseModel):
    """合婚分析請求"""
    person_a: BirthInfoModel
    person_b: BirthInfoModel

class MarriageDateRequest(BaseModel):
    """嫁娶擇日請求"""
    person_a: BirthInfoModel
    person_b: BirthInfoModel
    start_date: Optional[str] = Field(None, description="開始日期 YYYY-MM-DD")
    days: int = Field(90, ge=30, le=365, description="搜索天數")

# ============================================================
# API 端點
# ============================================================

@router.get("/info")
async def naming_info():
    """命名婚嫁 API 資訊"""
    return {
        "service": "北斗命數 - 命名婚嫁服務",
        "version": "1.0.0",
        "modules_loaded": MODULES_LOADED,
        "endpoints": {
            "analyze_name": "POST /api/v1/naming/analyze - 姓名分析",
            "baby_naming": "POST /api/v1/naming/baby - 新生兒命名",
            "compare_rename": "POST /api/v1/naming/rename - 改名比對",
            "company_analyze": "POST /api/v1/naming/company/analyze - 公司名分析",
            "company_suggest": "POST /api/v1/naming/company/suggest - 公司名建議",
            "marriage_match": "POST /api/v1/naming/marriage/match - 合婚分析",
            "marriage_date": "POST /api/v1/naming/marriage/date - 嫁娶擇日",
        }
    }

@router.post("/analyze")
async def analyze_name(request: NameAnalyzeRequest):
    """
    姓名分析（配合八字）
    
    分析姓名的五格、三才、總格吉凶，
    如果提供出生資訊，會配合八字喜用神分析。
    """
    if not MODULES_LOADED or not naming_api:
        raise HTTPException(503, "命名模組未載入")
    
    try:
        birth_dict = request.birth_info.dict() if request.birth_info else None
        result = naming_api.analyze_name(
            surname=request.surname,
            given_name=request.given_name,
            birth_info=birth_dict
        )
        return result
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/baby")
async def suggest_baby_names(request: BabyNamingRequest):
    """
    新生兒命名建議
    
    根據出生八字，配合五行喜用神，
    生成適合的名字建議。
    """
    if not MODULES_LOADED or not naming_api:
        raise HTTPException(503, "命名模組未載入")
    
    try:
        result = naming_api.suggest_baby_names(
            surname=request.surname,
            birth_info=request.birth_info.dict(),
            gender=request.gender,
            count=request.count
        )
        return result
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/rename")
async def compare_rename(request: RenameCompareRequest):
    """
    改名比對
    
    比較舊名與新名的五格變化，
    評估改名的優劣。
    """
    if not MODULES_LOADED or not naming_api:
        raise HTTPException(503, "命名模組未載入")
    
    try:
        birth_dict = request.birth_info.dict() if request.birth_info else None
        result = naming_api.compare_rename(
            surname=request.surname,
            old_name=request.old_name,
            new_name=request.new_name,
            birth_info=birth_dict
        )
        return result
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/company/analyze")
async def analyze_company_name(request: CompanyNameRequest):
    """
    公司行號名稱分析
    
    分析公司名的總筆畫、吉凶數理、
    與行業的五行配合度。
    """
    if not MODULES_LOADED or not naming_api:
        raise HTTPException(503, "命名模組未載入")
    
    try:
        result = naming_api.analyze_company_name(
            company_name=request.company_name,
            industry=request.industry
        )
        return result
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/company/suggest")
async def suggest_company_names(request: CompanySuggestRequest):
    """
    公司行號命名建議
    
    根據基礎概念和行業，
    生成吉利的公司名建議。
    """
    if not MODULES_LOADED or not naming_api:
        raise HTTPException(503, "命名模組未載入")
    
    try:
        result = naming_api.suggest_company_names(
            base_name=request.base_name,
            industry=request.industry,
            count=request.count
        )
        return result
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/marriage/match")
async def analyze_marriage_match(request: MarriageMatchRequest):
    """
    合婚分析（雙盤匹配）
    
    分析兩人八字的：
    - 五行相生相剋
    - 日主互動關係
    - 十神配合度
    - 整體相容度評分
    """
    if not MODULES_LOADED or not naming_api:
        raise HTTPException(503, "命名模組未載入")
    
    try:
        result = naming_api.analyze_marriage_match(
            person_a=request.person_a.dict(),
            person_b=request.person_b.dict()
        )
        return result
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/marriage/date")
async def find_marriage_dates(request: MarriageDateRequest):
    """
    嫁娶擇日擇時
    
    根據兩人八字，在指定時間範圍內
    尋找適合嫁娶的吉日良辰。
    
    考慮因素：
    - 黃道吉日
    - 沖煞避忌
    - 雙方八字喜用
    - 時辰吉凶
    """
    if not MODULES_LOADED or not naming_api:
        raise HTTPException(503, "命名模組未載入")
    
    try:
        result = naming_api.find_marriage_dates(
            person_a=request.person_a.dict(),
            person_b=request.person_b.dict(),
            start_date=request.start_date,
            days=request.days
        )
        return result
    except Exception as e:
        raise HTTPException(400, str(e))

# ============================================================
# 註冊函數
# ============================================================

def register_naming_routes(app):
    """註冊命名婚嫁路由到主應用"""
    app.include_router(router)
    print("✅ 命名婚嫁 API 路由已註冊")
