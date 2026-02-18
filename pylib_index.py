#!/usr/bin/env python3
"""
pylib_index.py - 北斗命數 PYLIB 程式化索引
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
PYLIB First 原則：先查現有工具，不重造輪子
本索引提供程式化的模組查詢和依賴管理
═══════════════════════════════════════════════════════════════════════

XTF Task Chain
@11星協作：@星殼(架構) @理樞(盤點)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum

# ════════════════════════════════════════════════════════════════════
# 狀態定義
# ════════════════════════════════════════════════════════════════════

class ModuleStatus(Enum):
    CORE = "core"           # 核心模組，必須保留
    EXTEND = "extend"       # 擴展模組，建議保留
    LEGACY = "legacy"       # 舊版模組，可替換
    MERGED = "merged"       # 已整合，可刪除
    ARCHIVE = "archive"     # 歸檔，歷史參考

class ModuleCategory(Enum):
    ENGINE = "engine"           # 核心引擎
    DATE = "date"               # 日期選擇
    NAMING = "naming"           # 命名系統
    REPORT = "report"           # 報告生成
    AUTH = "auth"               # 認證授權
    DATABASE = "database"       # 數據庫
    API = "api"                 # API 路由
    TRANSLATION = "translation" # 翻譯配置
    ANALYZER = "analyzer"       # 分析工具
    FRONTEND = "frontend"       # 前端管理
    PAYMENT = "payment"         # 支付商業
    YIJING = "yijing"           # 易經卦象
    UTILITY = "utility"         # 工具類

# ════════════════════════════════════════════════════════════════════
# 模組定義
# ════════════════════════════════════════════════════════════════════

@dataclass
class PyModule:
    """Python 模組定義"""
    name: str                           # 文件名（不含 .py）
    lines: int                          # 代碼行數
    category: ModuleCategory            # 分類
    status: ModuleStatus                # 狀態
    description: str                    # 描述
    replaces: List[str] = field(default_factory=list)      # 取代哪些舊模組
    depends_on: List[str] = field(default_factory=list)    # 依賴哪些模組
    replaced_by: Optional[str] = None   # 被哪個模組取代

# ════════════════════════════════════════════════════════════════════
# PYLIB 核心索引
# ════════════════════════════════════════════════════════════════════

PYLIB_MODULES: Dict[str, PyModule] = {
    # ─────────────────────────────────────────────────────────────────
    # L0 核心入口 (3 files)
    # ─────────────────────────────────────────────────────────────────
    "app": PyModule(
        name="app",
        lines=330,
        category=ModuleCategory.API,
        status=ModuleStatus.CORE,
        description="統一入口，整合所有 API",
        replaces=[],
        depends_on=["config", "db_unified", "main_api", "frontend_app"],
    ),
    "config": PyModule(
        name="config",
        lines=312,
        category=ModuleCategory.UTILITY,
        status=ModuleStatus.CORE,
        description="配置管理，環境變數載入",
        depends_on=[],
    ),
    "db_unified": PyModule(
        name="db_unified",
        lines=1137,
        category=ModuleCategory.DATABASE,
        status=ModuleStatus.CORE,
        description="統一數據庫 + JWT 認證",
        replaces=[],
        depends_on=["config"],
    ),
    
    # ─────────────────────────────────────────────────────────────────
    # 核心引擎
    # ─────────────────────────────────────────────────────────────────
    "bazi_base": PyModule(
        name="bazi_base",
        lines=812,
        category=ModuleCategory.ENGINE,
        status=ModuleStatus.CORE,
        description="八字基礎計算",
        replaces=["bazi_engine"],
        depends_on=["lunar_calendar_v2"],
    ),
    "bazi_advanced": PyModule(
        name="bazi_advanced",
        lines=565,
        category=ModuleCategory.ENGINE,
        status=ModuleStatus.CORE,
        description="八字進階分析（格局、用神）",
        depends_on=["bazi_base", "wuxing_analyzer", "geju_analyzer"],
    ),
    "ziwei_engine_v1": PyModule(
        name="ziwei_engine_v1",
        lines=665,
        category=ModuleCategory.ENGINE,
        status=ModuleStatus.CORE,
        description="紫微斗數排盤",
        depends_on=["lunar_calendar_v2"],
    ),
    "ziwei_advanced": PyModule(
        name="ziwei_advanced",
        lines=541,
        category=ModuleCategory.ENGINE,
        status=ModuleStatus.CORE,
        description="紫微進階分析",
        depends_on=["ziwei_engine_v1", "sihua_translation"],
    ),
    "meihua_engine": PyModule(
        name="meihua_engine",
        lines=336,
        category=ModuleCategory.ENGINE,
        status=ModuleStatus.CORE,
        description="梅花易數起卦、解卦",
        depends_on=["yijing_gua_translation"],
    ),
    "qimen_engine_v1": PyModule(
        name="qimen_engine_v1",
        lines=553,
        category=ModuleCategory.ENGINE,
        status=ModuleStatus.CORE,
        description="奇門遁甲排盤",
        depends_on=["lunar_calendar_v2"],
    ),
    
    # ─────────────────────────────────────────────────────────────────
    # 日期選擇
    # ─────────────────────────────────────────────────────────────────
    "date_base": PyModule(
        name="date_base",
        lines=950,
        category=ModuleCategory.DATE,
        status=ModuleStatus.CORE,
        description="擇日基礎框架",
        depends_on=["lunar_calendar_v2", "bazi_base"],
    ),
    "marry_date": PyModule(
        name="marry_date",
        lines=611,
        category=ModuleCategory.DATE,
        status=ModuleStatus.CORE,
        description="嫁娶擇日",
        depends_on=["date_base"],
    ),
    "ground_date": PyModule(
        name="ground_date",
        lines=709,
        category=ModuleCategory.DATE,
        status=ModuleStatus.CORE,
        description="動土擇日",
        depends_on=["date_base"],
    ),
    "event_date": PyModule(
        name="event_date",
        lines=467,
        category=ModuleCategory.DATE,
        status=ModuleStatus.CORE,
        description="事件擇日（開市、搬家）",
        depends_on=["date_base"],
    ),
    
    # ─────────────────────────────────────────────────────────────────
    # 命名系統
    # ─────────────────────────────────────────────────────────────────
    "naming_master": PyModule(
        name="naming_master",
        lines=1117,
        category=ModuleCategory.NAMING,
        status=ModuleStatus.CORE,
        description="命名主引擎",
        replaces=["name_engine", "naming_enhanced"],
        depends_on=["bazi_base", "wuxing_analyzer"],
    ),
    "naming_selector_v3": PyModule(
        name="naming_selector_v3",
        lines=822,
        category=ModuleCategory.NAMING,
        status=ModuleStatus.CORE,
        description="命名選擇器 v3",
        replaces=["naming_by_bazi"],
        depends_on=["naming_master"],
    ),
    "bazi_naming_selector": PyModule(
        name="bazi_naming_selector",
        lines=916,
        category=ModuleCategory.NAMING,
        status=ModuleStatus.CORE,
        description="八字命名選擇器",
        replaces=["bazi_naming_v2"],
        depends_on=["bazi_base", "naming_master"],
    ),
    
    # ─────────────────────────────────────────────────────────────────
    # 報告生成
    # ─────────────────────────────────────────────────────────────────
    "pdf_report_api": PyModule(
        name="pdf_report_api",
        lines=858,
        category=ModuleCategory.REPORT,
        status=ModuleStatus.CORE,
        description="PDF 報告 API",
        replaces=["pdf_generator"],
        depends_on=["report_generator"],
    ),
    "report_generator": PyModule(
        name="report_generator",
        lines=831,
        category=ModuleCategory.REPORT,
        status=ModuleStatus.CORE,
        description="報告生成器",
        replaces=["report_generator_v1", "report_generator_v2"],
        depends_on=["bazi_base", "ziwei_engine_v1"],
    ),
    
    # ─────────────────────────────────────────────────────────────────
    # API
    # ─────────────────────────────────────────────────────────────────
    "main_api": PyModule(
        name="main_api",
        lines=711,
        category=ModuleCategory.API,
        status=ModuleStatus.CORE,
        description="命理 API 端點",
        depends_on=["bazi_base", "ziwei_engine_v1", "meihua_engine"],
    ),
    "frontend_app": PyModule(
        name="frontend_app",
        lines=1085,
        category=ModuleCategory.FRONTEND,
        status=ModuleStatus.CORE,
        description="前端應用",
        depends_on=["config"],
    ),
    "admin": PyModule(
        name="admin",
        lines=453,
        category=ModuleCategory.FRONTEND,
        status=ModuleStatus.CORE,
        description="管理後台",
        depends_on=["db_unified", "config"],
    ),
    "payment_service": PyModule(
        name="payment_service",
        lines=465,
        category=ModuleCategory.PAYMENT,
        status=ModuleStatus.CORE,
        description="支付服務（綠界/藍新）",
        depends_on=["config"],
    ),
    
    # ─────────────────────────────────────────────────────────────────
    # 分析工具
    # ─────────────────────────────────────────────────────────────────
    "wuxing_core": PyModule(
        name="wuxing_core",
        lines=297,
        category=ModuleCategory.ANALYZER,
        status=ModuleStatus.CORE,
        description="五行核心計算",
        depends_on=[],
    ),
    "wuxing_analyzer": PyModule(
        name="wuxing_analyzer",
        lines=352,
        category=ModuleCategory.ANALYZER,
        status=ModuleStatus.CORE,
        description="五行分析",
        depends_on=["wuxing_core"],
    ),
    "geju_analyzer": PyModule(
        name="geju_analyzer",
        lines=352,
        category=ModuleCategory.ANALYZER,
        status=ModuleStatus.CORE,
        description="格局分析",
        depends_on=["bazi_base"],
    ),
    "liunian_analyzer": PyModule(
        name="liunian_analyzer",
        lines=349,
        category=ModuleCategory.ANALYZER,
        status=ModuleStatus.CORE,
        description="流年分析",
        depends_on=["bazi_base", "dayun_calculator"],
    ),
    "relation_analyzer": PyModule(
        name="relation_analyzer",
        lines=392,
        category=ModuleCategory.ANALYZER,
        status=ModuleStatus.CORE,
        description="關係分析",
        depends_on=["bazi_base"],
    ),
    "chart_matching": PyModule(
        name="chart_matching",
        lines=487,
        category=ModuleCategory.ANALYZER,
        status=ModuleStatus.CORE,
        description="命盤配對",
        depends_on=["bazi_base", "ziwei_engine_v1"],
    ),
    "dayun_calculator": PyModule(
        name="dayun_calculator",
        lines=301,
        category=ModuleCategory.ANALYZER,
        status=ModuleStatus.CORE,
        description="大運計算",
        depends_on=["bazi_base"],
    ),
    
    # ─────────────────────────────────────────────────────────────────
    # 翻譯配置
    # ─────────────────────────────────────────────────────────────────
    "field_translation_complete": PyModule(
        name="field_translation_complete",
        lines=708,
        category=ModuleCategory.TRANSLATION,
        status=ModuleStatus.CORE,
        description="完整欄位翻譯",
        replaces=["field_translation", "field_translation_v2", "field_translation_v3"],
        depends_on=[],
    ),
    "yijing_gua_translation": PyModule(
        name="yijing_gua_translation",
        lines=666,
        category=ModuleCategory.TRANSLATION,
        status=ModuleStatus.CORE,
        description="64卦翻譯",
        depends_on=[],
    ),
    "yijing_yao_translation": PyModule(
        name="yijing_yao_translation",
        lines=573,
        category=ModuleCategory.TRANSLATION,
        status=ModuleStatus.CORE,
        description="爻辭翻譯",
        depends_on=[],
    ),
    "sihua_translation": PyModule(
        name="sihua_translation",
        lines=571,
        category=ModuleCategory.TRANSLATION,
        status=ModuleStatus.CORE,
        description="四化翻譯",
        depends_on=[],
    ),
    "shensha_translation": PyModule(
        name="shensha_translation",
        lines=511,
        category=ModuleCategory.TRANSLATION,
        status=ModuleStatus.CORE,
        description="神煞翻譯",
        depends_on=[],
    ),
    
    # ─────────────────────────────────────────────────────────────────
    # 工具類
    # ─────────────────────────────────────────────────────────────────
    "lunar_calendar_v2": PyModule(
        name="lunar_calendar_v2",
        lines=281,
        category=ModuleCategory.UTILITY,
        status=ModuleStatus.CORE,
        description="農曆轉換",
        depends_on=[],
    ),
    
    # ─────────────────────────────────────────────────────────────────
    # 安全/日誌 (3 files)
    # ─────────────────────────────────────────────────────────────────
    "security": PyModule(
        name="security",
        lines=281,
        category=ModuleCategory.UTILITY,
        status=ModuleStatus.CORE,
        description="安全中間件（限流、防注入）",
        depends_on=[],
    ),
    "logger": PyModule(
        name="logger",
        lines=303,
        category=ModuleCategory.UTILITY,
        status=ModuleStatus.CORE,
        description="結構化日誌系統",
        depends_on=[],
    ),
    "auth_jwt": PyModule(
        name="auth_jwt",
        lines=344,
        category=ModuleCategory.AUTH,
        status=ModuleStatus.EXTEND,
        description="JWT 認證工具",
        depends_on=["config"],
    ),
    # ─────────────────────────────────────────────────────────────────
    # 2026-02-18 新增模組 (8 files, 3526 lines)
    # ─────────────────────────────────────────────────────────────────
    "email_verification": PyModule(
        name="email_verification",
        lines=359,
        category=ModuleCategory.AUTH,
        status=ModuleStatus.CORE,
        description="Email 驗證（驗證碼生成/發送/校驗）",
        depends_on=["db_unified", "email_service"],
    ),
    "social_auth": PyModule(
        name="social_auth",
        lines=473,
        category=ModuleCategory.AUTH,
        status=ModuleStatus.CORE,
        description="社交登入（Google OAuth + LINE Login）",
        depends_on=["db_unified", "auth_jwt"],
    ),
    "subscription_service": PyModule(
        name="subscription_service",
        lines=513,
        category=ModuleCategory.PAYMENT,
        status=ModuleStatus.CORE,
        description="訂閱制服務（綠界定期定額）",
        depends_on=["db_unified", "payment_service", "membership_service"],
    ),
    "contact_support": PyModule(
        name="contact_support",
        lines=521,
        category=ModuleCategory.API,
        status=ModuleStatus.CORE,
        description="客服支援（工單系統+Email通知）",
        depends_on=["db_unified", "email_service"],
    ),
    "report_sharing": PyModule(
        name="report_sharing",
        lines=303,
        category=ModuleCategory.REPORT,
        status=ModuleStatus.EXTEND,
        description="報告分享（限時/限次/密碼保護）",
        depends_on=["db_unified"],
    ),
    "referral_system": PyModule(
        name="referral_system",
        lines=467,
        category=ModuleCategory.PAYMENT,
        status=ModuleStatus.EXTEND,
        description="推薦系統（推薦碼/獎勵/病毒傳播）",
        depends_on=["db_unified", "email_service"],
    ),
    "privacy_first": PyModule(
        name="privacy_first",
        lines=421,
        category=ModuleCategory.AUTH,
        status=ModuleStatus.CORE,
        description="隱私優先（計算即焚/刪除帳戶/GDPR）",
        depends_on=["db_unified"],
    ),
    "classical_enhancement": PyModule(
        name="classical_enhancement",
        lines=1446,
        category=ModuleCategory.ENGINE,
        status=ModuleStatus.CORE,
        description="典籍增強v2.1（三層詮釋+十神+六親+星曜+八卦+格局+宮位=62白話+場損診斷+XTFS）",
        depends_on=[],
    ),
    "enhanced_analysis_api": PyModule(
        name="enhanced_analysis_api",
        lines=359,
        category=ModuleCategory.API,
        status=ModuleStatus.CORE,
        description="增強分析API（八字/紫微增強+十神白話API+星曜白話API+場損診斷API）",
        depends_on=["classical_enhancement", "bazi_base"],
    ),
    "report_enhancement": PyModule(
        name="report_enhancement",
        lines=217,
        category=ModuleCategory.REPORT,
        status=ModuleStatus.EXTEND,
        description="報告增強整合器（增強報告內容+白話區塊+場論區塊+方法論標記）",
        depends_on=["classical_enhancement"],
    ),
    "methodology_core": PyModule(
        name="methodology_core",
        lines=155,
        category=ModuleCategory.ENGINE,
        status=ModuleStatus.CORE,
        description="方法論核心（織明揭示+XTF-DAO+場論人際v3.6+核心原則）",
        depends_on=[],
    ),
    "about_api": PyModule(
        name="about_api",
        lines=75,
        category=ModuleCategory.API,
        status=ModuleStatus.EXTEND,
        description="關於頁API（方法論/織明揭示/XTF/場論/開發者聲明）",
        depends_on=["methodology_core"],
    ),
    "frontend_components": PyModule(
        name="frontend_components",
        lines=364,
        category=ModuleCategory.FRONTEND,
        status=ModuleStatus.EXTEND,
        description="前端組件生成器（白話卡片HTML/React+CSS樣式+前端數據格式化）",
        depends_on=["classical_enhancement"],
    ),
    "pdf_vernacular_section": PyModule(
        name="pdf_vernacular_section",
        lines=113,
        category=ModuleCategory.REPORT,
        status=ModuleStatus.EXTEND,
        description="PDF白話區塊（十神/格局/宮位/八卦表格數據+方法論說明）",
        depends_on=["classical_enhancement"],
    ),
    "test_enhanced_api": PyModule(
        name="test_enhanced_api",
        lines=185,
        category=ModuleCategory.ANALYZER,
        status=ModuleStatus.EXTEND,
        description="增強API測試套件（classical/methodology/frontend/pdf測試）",
        depends_on=["classical_enhancement", "methodology_core", "frontend_components", "pdf_vernacular_section"],
    ),
}

# ════════════════════════════════════════════════════════════════════
# PYLIB 查詢函數
# ════════════════════════════════════════════════════════════════════

def get_module(name: str) -> Optional[PyModule]:
    """獲取模組資訊"""
    return PYLIB_MODULES.get(name.replace(".py", ""))

def get_core_modules() -> List[PyModule]:
    """獲取所有核心模組"""
    return [m for m in PYLIB_MODULES.values() if m.status == ModuleStatus.CORE]

def get_modules_by_category(category: ModuleCategory) -> List[PyModule]:
    """按分類獲取模組"""
    return [m for m in PYLIB_MODULES.values() if m.category == category]

def get_dependencies(name: str, recursive: bool = True) -> Set[str]:
    """獲取模組依賴"""
    module = get_module(name)
    if not module:
        return set()
    
    deps = set(module.depends_on)
    
    if recursive:
        for dep in list(deps):
            deps.update(get_dependencies(dep, recursive=True))
    
    return deps

def find_replacement(old_name: str) -> Optional[str]:
    """查找舊模組的替代品"""
    old_name = old_name.replace(".py", "")
    for name, module in PYLIB_MODULES.items():
        if old_name in module.replaces:
            return name
    return None

def pylib_stats() -> Dict:
    """PYLIB 統計"""
    modules = list(PYLIB_MODULES.values())
    return {
        "total": len(modules),
        "core": len([m for m in modules if m.status == ModuleStatus.CORE]),
        "total_lines": sum(m.lines for m in modules),
        "by_category": {
            cat.value: len([m for m in modules if m.category == cat])
            for cat in ModuleCategory
        },
    }

# ════════════════════════════════════════════════════════════════════
# 測試
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  PYLIB 索引測試")
    print("=" * 60)
    
    stats = pylib_stats()
    print(f"\n【統計】")
    print(f"  總模組數: {stats['total']}")
    print(f"  核心模組: {stats['core']}")
    print(f"  總代碼行: {stats['total_lines']:,}")
    
    print(f"\n【按分類】")
    for cat, count in stats['by_category'].items():
        if count > 0:
            print(f"  {cat}: {count}")
    
    print(f"\n【依賴示例：app.py】")
    deps = get_dependencies("app")
    print(f"  依賴: {deps}")
    
    print(f"\n【替代查詢：user_auth】")
    replacement = find_replacement("user_auth")
    print(f"  替代品: {replacement}")
    
    print("\n" + "=" * 60)
    print("✅ PYLIB 索引測試完成")
    print("=" * 60)
