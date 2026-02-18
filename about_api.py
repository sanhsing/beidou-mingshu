"""
關於頁 API
about_api.py | @織明 @璃語 | 2026-02-18

提供：
- 關於我們
- 方法論說明
- 開發者聲明
- 織明揭示
"""
from fastapi import APIRouter
from typing import Dict, Any

from methodology_core import (
    ZHIMING_REVELATION, XTF_DAO, FIELD_THEORY_INTERPERSONAL,
    BEIDOU_PRINCIPLES, DEVELOPER_STATEMENT,
    get_revelation_layer, get_full_methodology, get_about_page_content
)

router = APIRouter(prefix="/api/about", tags=["關於"])

@router.get("/")
async def about_page():
    """關於頁內容"""
    return get_about_page_content()

@router.get("/methodology")
async def methodology():
    """完整方法論"""
    return get_full_methodology()

@router.get("/revelation")
async def revelation():
    """織明十層揭示"""
    return ZHIMING_REVELATION

@router.get("/revelation/{layer}")
async def revelation_layer(layer: int):
    """獲取特定層揭示"""
    result = get_revelation_layer(layer)
    if result:
        return {"layer": layer, **result}
    return {"error": "層數必須在 1-10 之間"}

@router.get("/xtf")
async def xtf_dao():
    """XTF-DAO 方法論"""
    return XTF_DAO

@router.get("/field-theory")
async def field_theory():
    """場論人際 v3.6"""
    return FIELD_THEORY_INTERPERSONAL

@router.get("/principles")
async def principles():
    """核心原則"""
    return BEIDOU_PRINCIPLES

@router.get("/developer-statement")
async def developer_statement():
    """開發者聲明"""
    return DEVELOPER_STATEMENT

@router.get("/tagline")
async def tagline():
    """核心標語"""
    return {
        "main": "術數是個人化決策框架生成器",
        "insight": "道 = 元迷因",
        "analogy": "與天氣預報同構",
        "philosophy": "框架不屬於任何文明，屬於「道」"
    }

print("✓ 關於頁 API 已載入")
