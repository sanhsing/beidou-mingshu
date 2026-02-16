"""
易經 API 路由 yijing_api.py v1.0
================================
XTF任務：融-F | 執行星：光蘊（統籌）
整合日期：2026-02-08

提供易經64卦、384爻的 RESTful API
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel

from yijing_gua_translation import GUA_64, get_gua_info, get_gua_by_name, translate_gua, generate_gua_report
from yijing_yao_translation import YAO_384, get_yao_info, translate_yao, generate_yao_report, get_all_yao_for_gua

# ============================================================
# Router
# ============================================================

router = APIRouter(prefix="/yijing", tags=["易經"])

# ============================================================
# Response Models
# ============================================================

class GuaResponse(BaseModel):
    num: int
    name: str
    symbol: str
    full_name: str
    keyword: str
    vernacular: str
    field: str
    modern: str
    daxiang: str
    action: str
    warning: str

class YaoResponse(BaseModel):
    gua_num: int
    yao_pos: int
    yao_name: str
    text: str
    vernacular: str
    field: str
    action: str

class FullGuaResponse(BaseModel):
    gua: GuaResponse
    yao: List[YaoResponse]

# ============================================================
# Endpoints
# ============================================================

@router.get("/status")
async def get_yijing_status():
    """獲取易經模組狀態"""
    return {
        "module": "yijing",
        "version": "1.0",
        "gua_count": len(GUA_64),
        "yao_count": len(YAO_384),
        "coverage": {
            "gua": "64/64 (100%)",
            "yao": f"{len(YAO_384)}/384 ({len(YAO_384)*100//384}%)"
        }
    }

@router.get("/gua/{gua_num}")
async def get_gua(gua_num: int):
    """獲取指定卦的信息"""
    if gua_num < 1 or gua_num > 64:
        raise HTTPException(status_code=400, detail="卦號必須在1-64之間")
    
    gua = generate_gua_report(gua_num)
    if "error" in gua:
        raise HTTPException(status_code=404, detail=gua["error"])
    
    return gua

@router.get("/gua/name/{name}")
async def get_gua_by_name_endpoint(name: str):
    """通過卦名獲取卦信息"""
    gua = get_gua_by_name(name)
    if not gua:
        raise HTTPException(status_code=404, detail=f"未找到卦：{name}")
    return gua

@router.get("/gua/{gua_num}/full")
async def get_full_gua(gua_num: int):
    """獲取完整卦象（含六爻）"""
    if gua_num < 1 or gua_num > 64:
        raise HTTPException(status_code=400, detail="卦號必須在1-64之間")
    
    gua = generate_gua_report(gua_num)
    if "error" in gua:
        raise HTTPException(status_code=404, detail=gua["error"])
    
    yao_list = get_all_yao_for_gua(gua_num)
    
    return {
        "gua": gua,
        "yao": yao_list,
        "yao_count": len(yao_list)
    }

@router.get("/yao/{gua_num}/{yao_pos}")
async def get_yao(gua_num: int, yao_pos: int):
    """獲取指定爻的信息"""
    if gua_num < 1 or gua_num > 64:
        raise HTTPException(status_code=400, detail="卦號必須在1-64之間")
    if yao_pos < 1 or yao_pos > 6:
        raise HTTPException(status_code=400, detail="爻位必須在1-6之間")
    
    yao = generate_yao_report(gua_num, yao_pos)
    if "error" in yao:
        raise HTTPException(status_code=404, detail=yao["error"])
    
    return yao

@router.get("/gua/list")
async def list_all_gua():
    """列出所有64卦"""
    return [
        {
            "num": num,
            "name": gua["name"],
            "symbol": gua["symbol"],
            "full_name": gua["full_name"],
            "keyword": gua["keyword"]
        }
        for num, gua in GUA_64.items()
    ]

@router.get("/translate/gua/{gua_num}")
async def translate_gua_endpoint(gua_num: int):
    """獲取卦的白話翻譯文本"""
    if gua_num < 1 or gua_num > 64:
        raise HTTPException(status_code=400, detail="卦號必須在1-64之間")
    
    text = translate_gua(gua_num)
    return {"gua_num": gua_num, "translation": text}

@router.get("/translate/yao/{gua_num}/{yao_pos}")
async def translate_yao_endpoint(gua_num: int, yao_pos: int):
    """獲取爻的白話翻譯文本"""
    if gua_num < 1 or gua_num > 64:
        raise HTTPException(status_code=400, detail="卦號必須在1-64之間")
    if yao_pos < 1 or yao_pos > 6:
        raise HTTPException(status_code=400, detail="爻位必須在1-6之間")
    
    text = translate_yao(gua_num, yao_pos)
    return {"gua_num": gua_num, "yao_pos": yao_pos, "translation": text}
