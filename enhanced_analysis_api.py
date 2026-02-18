"""
增強版分析 API
enhanced_analysis_api.py | @星殼 @理樞 | 2026-02-18

整合 classical_enhancement v2.0 三層詮釋體系：
- 古典原文
- 白話翻譯
- 場論詮釋
- SWOT 決策
- AI 建議
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# 導入核心模組
try:
    from bazi_base import analyze_bazi, BaziChart
    HAS_BAZI = True
except ImportError:
    HAS_BAZI = False

try:
    from ziwei_engine_v1 import create_ziwei_chart, ZiWeiChart, field_translation
    HAS_ZIWEI = True
except ImportError:
    HAS_ZIWEI = False
    create_ziwei_chart = None
    ZiWeiChart = None

# 導入增強模組
from classical_enhancement import (
    enhance_analysis_v2,
    get_shishen_glossary,
    get_ziwei_star_glossary,
    get_all_shishen_vernacular,
    get_all_ziwei_vernacular,
    SHISHEN_GLOSSARY,
    ZIWEI_STAR_GLOSSARY,
    SHISHEN_FIELD_DIAGNOSIS,
    SHISHEN_XTFS_MAPPING
)

router = APIRouter(prefix="/api/enhanced", tags=["增強分析"])

# ════════════════════════════════════════════════════════════════════
# 請求模型
# ════════════════════════════════════════════════════════════════════

class BaziEnhancedRequest(BaseModel):
    """增強版八字分析請求"""
    year_gz: str          # 年柱干支
    month_gz: str         # 月柱干支
    day_gz: str           # 日柱干支
    hour_gz: str          # 時柱干支
    include_classics: bool = True      # 包含典籍引用
    include_glossary: bool = True      # 包含白話翻譯
    include_swot: bool = True          # 包含 SWOT 分析
    include_ai_advice: bool = True     # 包含 AI 建議

class ZiweiEnhancedRequest(BaseModel):
    """增強版紫微分析請求"""
    year: int
    month: int
    day: int
    hour: int
    gender: str = "男"
    include_classics: bool = True
    include_glossary: bool = True
    include_swot: bool = True
    include_ai_advice: bool = True

class SymptomDiagnosisRequest(BaseModel):
    """場損診斷請求"""
    symptoms: List[str]   # 感受列表

# ════════════════════════════════════════════════════════════════════
# 八字增強分析
# ════════════════════════════════════════════════════════════════════

@router.post("/bazi/analyze")
async def bazi_enhanced_analyze(req: BaziEnhancedRequest):
    """
    增強版八字分析
    
    返回：
    - 基礎八字資訊
    - 典籍原文引用
    - 十神白話翻譯
    - 場論詮釋
    - SWOT 決策分析
    - AI 建議
    """
    if not HAS_BAZI:
        raise HTTPException(500, "八字模組未啟用")
    
    try:
        # 基礎分析
        chart = analyze_bazi(req.year_gz, req.month_gz, req.day_gz, req.hour_gz)
        
        # 提取十神列表
        shishen_list = []
        for pillar in chart.pillars:
            if pillar and pillar.gan:
                ss = chart.calc_ten_god(pillar.gan)
                if ss and ss not in shishen_list:
                    shishen_list.append(ss)
        
        # 基礎結果
        base_result = {
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
            "shishen": shishen_list,
            "wx_distribution": chart.wx_distribution,
        }
        
        # 增強分析
        enhanced = enhance_analysis_v2(
            analysis_type="bazi",
            raw_result=base_result,
            include_classics=req.include_classics,
            include_glossary=req.include_glossary,
            include_swot=req.include_swot,
            include_ai_advice=req.include_ai_advice
        )
        
        return enhanced
        
    except Exception as e:
        raise HTTPException(400, f"分析錯誤：{e}")

@router.get("/bazi/shishen/{name}")
async def get_shishen_detail(name: str):
    """
    獲取十神詳細白話翻譯
    
    返回：
    - 古典說法
    - 白話翻譯
    - 場論詮釋
    - 場態分析（增強/過強/過弱）
    - 調場方法
    - XTFS 映射
    """
    result = get_shishen_glossary(name)
    if not result:
        raise HTTPException(404, f"十神 '{name}' 不存在")
    return result

@router.get("/bazi/shishen")
async def list_all_shishen():
    """
    列出所有十神白話翻譯
    """
    return {
        "count": len(SHISHEN_GLOSSARY),
        "shishen": get_all_shishen_vernacular(),
        "xtfs_mapping": SHISHEN_XTFS_MAPPING
    }

# ════════════════════════════════════════════════════════════════════
# 紫微增強分析
# ════════════════════════════════════════════════════════════════════

@router.post("/ziwei/analyze")
async def ziwei_enhanced_analyze(req: ZiweiEnhancedRequest):
    """
    增強版紫微分析
    
    注意：需要農曆資料，此 API 暫時簡化
    
    返回：
    - 基礎紫微命盤
    - 典籍原文引用
    - 星曜白話翻譯
    - 場論詮釋
    - SWOT 決策分析
    - AI 建議
    """
    if not HAS_ZIWEI:
        raise HTTPException(500, "紫微模組未啟用")
    
    try:
        # 注意：create_ziwei_chart 需要農曆資料
        # 這裡暫時返回星曜白話詞典
        # TODO: 整合農曆轉換
        
        # 返回可用的星曜白話翻譯
        base_result = {
            "basic_info": {
                "year": req.year,
                "month": req.month,
                "day": req.day,
                "hour": req.hour,
                "gender": req.gender,
            },
            "stars": list(ZIWEI_STAR_GLOSSARY.keys()),  # 返回所有星曜名稱
            "note": "完整分析需提供農曆資料，目前返回星曜白話詞典"
        }
        
        # 增強分析
        enhanced = enhance_analysis_v2(
            analysis_type="ziwei",
            raw_result=base_result,
            include_classics=req.include_classics,
            include_glossary=req.include_glossary,
            include_swot=req.include_swot,
            include_ai_advice=req.include_ai_advice
        )
        
        return enhanced
        
    except Exception as e:
        raise HTTPException(400, f"分析錯誤：{e}")

@router.get("/ziwei/star/{name}")
async def get_star_detail(name: str):
    """
    獲取紫微星曜詳細白話翻譯
    
    返回：
    - 五行屬性
    - 古典含義
    - 白話翻譯
    - 場論詮釋
    - 現代職業
    - 優勢/風險
    """
    result = get_ziwei_star_glossary(name)
    if not result:
        raise HTTPException(404, f"星曜 '{name}' 不存在")
    return result

@router.get("/ziwei/stars")
async def list_all_stars():
    """
    列出所有紫微星曜白話翻譯
    """
    return {
        "count": len(ZIWEI_STAR_GLOSSARY),
        "stars": get_all_ziwei_vernacular()
    }

# ════════════════════════════════════════════════════════════════════
# 場損診斷
# ════════════════════════════════════════════════════════════════════

@router.post("/diagnose")
async def diagnose_field_issues(req: SymptomDiagnosisRequest):
    """
    根據感受診斷場損
    
    輸入感受列表，返回可能的十神場損和調場建議
    """
    results = []
    
    for symptom in req.symptoms:
        for key, diagnosis in SHISHEN_FIELD_DIAGNOSIS.items():
            if key in symptom or symptom in key:
                results.append({
                    "symptom": symptom,
                    "matched_key": key,
                    "diagnosis": diagnosis["diagnosis"],
                    "remedy": diagnosis["remedy"],
                    "action": diagnosis["action"]
                })
                break
        else:
            results.append({
                "symptom": symptom,
                "matched_key": None,
                "diagnosis": "無法診斷",
                "remedy": "建議詳細描述感受",
                "action": "可嘗試完整八字分析"
            })
    
    return {
        "count": len(results),
        "diagnoses": results,
        "available_symptoms": list(SHISHEN_FIELD_DIAGNOSIS.keys())
    }

@router.get("/diagnose/symptoms")
async def list_diagnosable_symptoms():
    """
    列出所有可診斷的感受
    """
    return {
        "count": len(SHISHEN_FIELD_DIAGNOSIS),
        "symptoms": SHISHEN_FIELD_DIAGNOSIS
    }

# ════════════════════════════════════════════════════════════════════
# 方法論說明
# ════════════════════════════════════════════════════════════════════

@router.get("/methodology")
async def get_methodology():
    """
    獲取三層詮釋體系說明
    """
    return {
        "name": "北斗命數三層詮釋體系",
        "version": "v2.0",
        "layers": {
            "layer_1": {
                "name": "古典原文",
                "description": "典籍引用，標明出處",
                "sources": ["淵海子平", "三命通會", "滴天髓", "紫微斗數全書"]
            },
            "layer_2": {
                "name": "白話翻譯",
                "description": "讓一般人看得懂",
                "example": "七殺 → 不講道理的壓力"
            },
            "layer_3": {
                "name": "場論詮釋",
                "description": "用現代語言重新理解",
                "example": "七殺 → 外部場對你的場進行衝擊性壓制"
            },
            "layer_4": {
                "name": "SWOT 分析",
                "description": "可操作的策略建議"
            },
            "layer_5": {
                "name": "AI 決策",
                "description": "多維度交叉驗證"
            }
        },
        "principle": "術數是個人化決策框架生成器，與天氣預報同構",
        "disclaimer": "提供機率性參考，不做命定式裁決"
    }

# ════════════════════════════════════════════════════════════════════
# 模組載入
# ════════════════════════════════════════════════════════════════════

print("✓ 增強分析 API 已載入")
print(f"  - 八字增強: {'✓' if HAS_BAZI else '✗'}")
print(f"  - 紫微增強: {'✓' if HAS_ZIWEI else '✗'}")
print(f"  - 十神白話: {len(SHISHEN_GLOSSARY)} 個")
print(f"  - 星曜白話: {len(ZIWEI_STAR_GLOSSARY)} 個")

# ════════════════════════════════════════════════════════════════════
# 新增端點：八卦/格局/宮位
# ════════════════════════════════════════════════════════════════════

from classical_enhancement import (
    get_bagua_glossary, get_geju_glossary, get_gongwei_glossary,
    get_all_bagua_vernacular, get_all_geju_vernacular, get_all_gongwei_vernacular,
    get_gongwei_opposite_pairs,
    BAGUA_GLOSSARY, GEJU_GLOSSARY, GONGWEI_GLOSSARY
)

@router.get("/meihua/bagua/{name}")
async def get_bagua_detail(name: str):
    """獲取八卦白話翻譯"""
    result = get_bagua_glossary(name)
    if not result:
        raise HTTPException(404, f"八卦 '{name}' 不存在")
    return result

@router.get("/meihua/bagua")
async def list_all_bagua():
    """列出所有八卦白話"""
    return {
        "count": len(BAGUA_GLOSSARY),
        "bagua": get_all_bagua_vernacular()
    }

@router.get("/bazi/geju/{name}")
async def get_geju_detail(name: str):
    """獲取格局白話翻譯"""
    result = get_geju_glossary(name)
    if not result:
        raise HTTPException(404, f"格局 '{name}' 不存在")
    return result

@router.get("/bazi/geju")
async def list_all_geju():
    """列出所有格局白話"""
    return {
        "count": len(GEJU_GLOSSARY),
        "geju": get_all_geju_vernacular()
    }

@router.get("/ziwei/gongwei/{name}")
async def get_gongwei_detail(name: str):
    """獲取宮位場論詮釋"""
    result = get_gongwei_glossary(name)
    if not result:
        raise HTTPException(404, f"宮位 '{name}' 不存在")
    return result

@router.get("/ziwei/gongwei")
async def list_all_gongwei():
    """列出所有宮位場論"""
    return {
        "count": len(GONGWEI_GLOSSARY),
        "gongwei": get_all_gongwei_vernacular(),
        "opposite_pairs": get_gongwei_opposite_pairs()
    }
