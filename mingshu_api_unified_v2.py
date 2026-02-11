#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mingshu_api_unified_v2.py - 北斗命數統一API入口 v2.0
====================================================
北斗七星文創 × 織明

整合所有功能模組的統一API入口
包含：基本版 + 專業版 + 進階版 (D1-D4)

XTF⁸ + XTFS + @11star 協作
執行星：織明(統籌) × 星殼(架構) × 璃語(介面)

📚 知識點：
    「統一入口 = 場的單一接觸點」
    「分層架構 = 功能場的組織方式」
"""

from flask import Flask, request, jsonify
from functools import wraps
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import sys
import os

# =============================================================================
# 模組動態載入
# =============================================================================

def safe_import(module_name: str, fallback=None):
    """安全導入模組"""
    try:
        return __import__(module_name)
    except ImportError:
        return fallback

# 核心引擎
try:
    from mingshu_engine_v1 import MingshuEngine
    ENGINE_AVAILABLE = True
except:
    ENGINE_AVAILABLE = False

# 流年合盤
try:
    from mingshu_liunian_hepan_v1 import LiunianEngine, HepanEngine
    LIUNIAN_AVAILABLE = True
except:
    LIUNIAN_AVAILABLE = False

# 擇日存儲
try:
    from mingshu_zeri_db_web_v1 import ZeriEngine, MingshuDB
    ZERI_AVAILABLE = True
except:
    ZERI_AVAILABLE = False

# 姓名嫁娶
try:
    from mingshu_naming_marriage_v1 import NameEngine, CompanyNameEngine, MarriageZeriEngine
    NAMING_AVAILABLE = True
except:
    NAMING_AVAILABLE = False

# 梅花PDF
try:
    from mingshu_meihua_pdf_v1 import MeihuaEngine, PDFGenerator
    MEIHUA_AVAILABLE = True
except:
    MEIHUA_AVAILABLE = False

# 商用套件
try:
    from mingshu_commercial_v1 import ConfigManager, AuthManager, HealthMonitor
    COMMERCIAL_AVAILABLE = True
except:
    COMMERCIAL_AVAILABLE = False

# 進階術數
try:
    from mingshu_advanced_pylib_v1 import MingshuAdvancedPylibAPI
    ADVANCED_AVAILABLE = True
except:
    ADVANCED_AVAILABLE = False

# 場論引擎
try:
    from field_engine_v1 import FieldEngine
    FIELD_AVAILABLE = True
except:
    FIELD_AVAILABLE = False


# =============================================================================
# 訂閱層級定義
# =============================================================================

class SubscriptionTier(Enum):
    """訂閱層級"""
    FREE = ("free", 0, 5)           # 免費試用，5次/天
    BASIC = ("basic", 69, 30)       # 基本版 NT$69/月，30次/月
    PRO = ("pro", 199, -1)          # 專業版 NT$199/月，無限
    ADVANCED = ("advanced", 399, -1) # 進階版 NT$399/月，無限+D1-D4

    def __init__(self, tier_name: str, price: int, quota: int):
        self.tier_name = tier_name
        self.price = price
        self.quota = quota


# API 端點層級映射
ENDPOINT_TIERS = {
    # 基本版端點
    "/api/bazi": "basic",
    "/api/ziwei": "basic",
    "/api/name/analyze": "basic",
    "/api/meihua/now": "basic",
    "/api/meihua/number": "basic",
    "/api/meihua/word": "basic",
    "/api/liunian": "basic",
    "/api/field": "basic",
    "/api/full": "basic",
    
    # 專業版端點
    "/api/yijing": "pro",
    "/api/now": "pro",
    "/api/name/baby": "pro",
    "/api/name/rename": "pro",
    "/api/company/analyze": "pro",
    "/api/company/suggest": "pro",
    "/api/marriage/match": "pro",
    "/api/marriage/dates": "pro",
    "/api/hepan": "pro",
    "/api/zeri": "pro",
    "/api/report/generate": "pro",
    
    # 進階版端點 (D1-D4)
    "/api/sihua": "advanced",
    "/api/sihua/feixing": "advanced",
    "/api/sihua/zihua": "advanced",
    "/api/qimen": "advanced",
    "/api/liuren": "advanced",
    "/api/fengshui": "advanced",
}

# 免費端點
FREE_ENDPOINTS = ["/", "/health", "/docs", "/api/pricing", "/api/status"]


# =============================================================================
# Flask 應用
# =============================================================================

class MingshuUnifiedAPIv2:
    """
    北斗命數統一API v2.0
    
    整合全部功能：基本版 + 專業版 + 進階版
    
    📚 知識點：
        統一入口 = 場的單一接觸點
        分層架構 = 功能場的組織方式
    """
    
    VERSION = "2.0.0"
    
    def __init__(self):
        self.app = Flask(__name__)
        
        # 初始化引擎
        self._init_engines()
        
        # 註冊中間件
        self._register_middleware()
        
        # 註冊路由
        self._register_routes()
    
    def _init_engines(self):
        """初始化所有引擎"""
        # 核心引擎
        self.mingshu = MingshuEngine() if ENGINE_AVAILABLE else None
        
        # 流年合盤
        self.liunian = LiunianEngine() if LIUNIAN_AVAILABLE else None
        self.hepan = HepanEngine() if LIUNIAN_AVAILABLE else None
        
        # 擇日存儲
        self.zeri = ZeriEngine() if ZERI_AVAILABLE else None
        self.db = MingshuDB() if ZERI_AVAILABLE else None
        
        # 姓名嫁娶
        self.name_engine = NameEngine() if NAMING_AVAILABLE else None
        self.company_engine = CompanyNameEngine() if NAMING_AVAILABLE else None
        self.marriage_engine = MarriageZeriEngine() if NAMING_AVAILABLE else None
        
        # 梅花PDF
        self.meihua = MeihuaEngine() if MEIHUA_AVAILABLE else None
        self.pdf = PDFGenerator() if MEIHUA_AVAILABLE else None
        
        # 進階術數
        self.advanced = MingshuAdvancedPylibAPI() if ADVANCED_AVAILABLE else None
        
        # 場論引擎
        self.field = FieldEngine() if FIELD_AVAILABLE else None
        
        # 商用組件
        self.config = ConfigManager() if COMMERCIAL_AVAILABLE else None
        self.auth = AuthManager() if COMMERCIAL_AVAILABLE else None
        self.health = HealthMonitor() if COMMERCIAL_AVAILABLE else None
    
    def _register_middleware(self):
        """註冊中間件"""
        @self.app.before_request
        def check_tier():
            """檢查訂閱層級"""
            path = request.path
            
            # 免費端點跳過
            if path in FREE_ENDPOINTS:
                return None
            
            # 獲取用戶層級
            tier = request.headers.get("X-Subscription-Tier", "free")
            
            # 獲取端點要求層級
            required = ENDPOINT_TIERS.get(path, "basic")
            
            # 層級順序
            tier_order = {"free": 0, "basic": 1, "pro": 2, "advanced": 3}
            
            if tier_order.get(tier, 0) < tier_order.get(required, 1):
                return jsonify({
                    "success": False,
                    "error": f"此端點需要 {required} 或更高層級",
                    "required_tier": required,
                    "your_tier": tier
                }), 403
            
            return None
        
        @self.app.after_request
        def add_headers(response):
            """添加響應頭"""
            response.headers["X-API-Version"] = self.VERSION
            response.headers["X-Powered-By"] = "Beidou-Mingshu"
            return response
    
    def _register_routes(self):
        """註冊所有路由"""
        
        # ===== 系統端點 =====
        
        @self.app.route("/")
        def index():
            """系統概覽"""
            return jsonify({
                "name": "北斗命數 API",
                "version": self.VERSION,
                "tiers": {
                    "basic": {"price": 69, "quota": 30, "endpoints": 9},
                    "pro": {"price": 199, "quota": "unlimited", "endpoints": 11},
                    "advanced": {"price": 399, "quota": "unlimited", "endpoints": 6}
                },
                "total_endpoints": len(ENDPOINT_TIERS),
                "documentation": "/docs"
            })
        
        @self.app.route("/health")
        def health():
            """健康檢查"""
            engines = {
                "mingshu": ENGINE_AVAILABLE,
                "liunian": LIUNIAN_AVAILABLE,
                "zeri": ZERI_AVAILABLE,
                "naming": NAMING_AVAILABLE,
                "meihua": MEIHUA_AVAILABLE,
                "advanced": ADVANCED_AVAILABLE,
                "field": FIELD_AVAILABLE,
                "commercial": COMMERCIAL_AVAILABLE
            }
            
            available = sum(engines.values())
            total = len(engines)
            
            return jsonify({
                "status": "healthy" if available >= 4 else "degraded",
                "engines": engines,
                "available": f"{available}/{total}",
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route("/api/status")
        def status():
            """API 狀態"""
            return jsonify({
                "success": True,
                "data": {
                    "version": self.VERSION,
                    "engines": {
                        "core": ENGINE_AVAILABLE,
                        "liunian_hepan": LIUNIAN_AVAILABLE,
                        "zeri_db": ZERI_AVAILABLE,
                        "naming_marriage": NAMING_AVAILABLE,
                        "meihua_pdf": MEIHUA_AVAILABLE,
                        "advanced_d1d4": ADVANCED_AVAILABLE,
                        "field_engine": FIELD_AVAILABLE,
                        "commercial": COMMERCIAL_AVAILABLE
                    },
                    "tiers": ["free", "basic", "pro", "advanced"],
                    "endpoints": {
                        "basic": 9,
                        "pro": 11,
                        "advanced": 6,
                        "total": len(ENDPOINT_TIERS)
                    }
                }
            })
        
        @self.app.route("/api/pricing")
        def pricing():
            """定價方案"""
            return jsonify({
                "success": True,
                "data": {
                    "basic": {
                        "name": "基本版",
                        "price": "NT$69/月",
                        "quota": "30次/月",
                        "features": [
                            "八字排盤",
                            "紫微斗數",
                            "姓名分析",
                            "梅花易數",
                            "流年運勢",
                            "場態分析",
                            "完整報告"
                        ]
                    },
                    "pro": {
                        "name": "專業版",
                        "price": "NT$199/月",
                        "quota": "無限查詢",
                        "features": [
                            "包含基本版所有功能",
                            "易經占卜",
                            "嬰兒命名",
                            "成人改名",
                            "公司命名",
                            "合婚分析",
                            "擇日服務",
                            "合盤分析",
                            "PDF報告"
                        ]
                    },
                    "advanced": {
                        "name": "進階版",
                        "price": "NT$399/月",
                        "quota": "無限查詢",
                        "features": [
                            "包含專業版所有功能",
                            "紫微四化飛星",
                            "奇門遁甲排盤",
                            "六壬神課起課",
                            "風水羅盤分析",
                            "場論深度解讀"
                        ]
                    }
                }
            })
        
        # ===== 基本版端點 =====
        
        @self.app.route("/api/bazi", methods=["POST"])
        def api_bazi():
            """八字排盤"""
            if not self.mingshu:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.mingshu.get_bazi(
                year=data.get("year"),
                month=data.get("month"),
                day=data.get("day"),
                hour=data.get("hour"),
                gender=data.get("gender", "male")
            )
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/ziwei", methods=["POST"])
        def api_ziwei():
            """紫微斗數"""
            if not self.mingshu:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.mingshu.get_ziwei(
                year=data.get("year"),
                month=data.get("month"),
                day=data.get("day"),
                hour=data.get("hour"),
                gender=data.get("gender", "male")
            )
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/field", methods=["POST"])
        def api_field():
            """場態分析"""
            if not self.mingshu:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.mingshu.analyze_field(
                year=data.get("year"),
                month=data.get("month"),
                day=data.get("day"),
                hour=data.get("hour")
            )
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/full", methods=["POST"])
        def api_full():
            """完整分析"""
            if not self.mingshu:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.mingshu.full_analysis(
                year=data.get("year"),
                month=data.get("month"),
                day=data.get("day"),
                hour=data.get("hour"),
                gender=data.get("gender", "male")
            )
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/name/analyze", methods=["POST"])
        def api_name_analyze():
            """姓名分析"""
            if not self.name_engine:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.name_engine.analyze(
                surname=data.get("surname"),
                given_name=data.get("given_name")
            )
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/meihua/now", methods=["GET"])
        def api_meihua_now():
            """梅花易數 - 當下起卦"""
            if not self.meihua:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            result = self.meihua.qigua_now()
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/meihua/number", methods=["POST"])
        def api_meihua_number():
            """梅花易數 - 數字起卦"""
            if not self.meihua:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.meihua.qigua_number(
                num1=data.get("num1"),
                num2=data.get("num2")
            )
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/meihua/word", methods=["POST"])
        def api_meihua_word():
            """梅花易數 - 文字起卦"""
            if not self.meihua:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.meihua.qigua_word(word=data.get("word"))
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/liunian", methods=["POST"])
        def api_liunian():
            """流年運勢"""
            if not self.liunian:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.liunian.analyze(
                year=data.get("year"),
                month=data.get("month"),
                day=data.get("day"),
                hour=data.get("hour"),
                target_year=data.get("target_year", datetime.now().year)
            )
            return jsonify({"success": True, "data": result})
        
        # ===== 專業版端點 =====
        
        @self.app.route("/api/yijing", methods=["POST"])
        def api_yijing():
            """易經占卜"""
            if not self.mingshu:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.mingshu.get_yijing(question=data.get("question"))
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/now", methods=["GET"])
        def api_now():
            """當下場態"""
            if not self.mingshu:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            result = self.mingshu.get_current_field()
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/name/baby", methods=["POST"])
        def api_name_baby():
            """嬰兒命名"""
            if not self.name_engine:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.name_engine.suggest_baby_names(
                surname=data.get("surname"),
                gender=data.get("gender"),
                birth_data=data.get("birth_data")
            )
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/name/rename", methods=["POST"])
        def api_name_rename():
            """成人改名"""
            if not self.name_engine:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.name_engine.suggest_rename(
                surname=data.get("surname"),
                current_name=data.get("current_name"),
                birth_data=data.get("birth_data")
            )
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/company/analyze", methods=["POST"])
        def api_company_analyze():
            """公司名分析"""
            if not self.company_engine:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.company_engine.analyze(name=data.get("name"))
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/company/suggest", methods=["POST"])
        def api_company_suggest():
            """公司命名建議"""
            if not self.company_engine:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.company_engine.suggest(
                industry=data.get("industry"),
                keywords=data.get("keywords", [])
            )
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/marriage/match", methods=["POST"])
        def api_marriage_match():
            """合婚分析"""
            if not self.marriage_engine:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.marriage_engine.analyze_match(
                person1=data.get("person1"),
                person2=data.get("person2")
            )
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/marriage/dates", methods=["POST"])
        def api_marriage_dates():
            """嫁娶擇日"""
            if not self.marriage_engine:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.marriage_engine.find_dates(
                person1=data.get("person1"),
                person2=data.get("person2"),
                start_date=data.get("start_date"),
                end_date=data.get("end_date")
            )
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/hepan", methods=["POST"])
        def api_hepan():
            """合盤分析"""
            if not self.hepan:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.hepan.analyze(
                person1=data.get("person1"),
                person2=data.get("person2")
            )
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/zeri", methods=["POST"])
        def api_zeri():
            """擇日服務"""
            if not self.zeri:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.zeri.find_dates(
                activity=data.get("activity"),
                birth_data=data.get("birth_data"),
                start_date=data.get("start_date"),
                end_date=data.get("end_date")
            )
            return jsonify({"success": True, "data": result})
        
        @self.app.route("/api/report/generate", methods=["POST"])
        def api_report_generate():
            """生成PDF報告"""
            if not self.pdf:
                return jsonify({"success": False, "error": "引擎未載入"}), 503
            
            data = request.get_json()
            result = self.pdf.generate(
                report_type=data.get("type"),
                data=data.get("data")
            )
            return jsonify({"success": True, "data": result})
        
        # ===== 進階版端點 (D1-D4) =====
        
        @self.app.route("/api/sihua", methods=["POST"])
        def api_sihua():
            """四化分析"""
            if not self.advanced:
                return jsonify({"success": False, "error": "進階引擎未載入"}), 503
            
            data = request.get_json()
            result = self.advanced.analyze_sihua(
                year_gan=data.get("year_gan"),
                star_positions=data.get("star_positions")
            )
            return jsonify(result)
        
        @self.app.route("/api/sihua/feixing", methods=["POST"])
        def api_feixing():
            """飛星分析"""
            if not self.advanced:
                return jsonify({"success": False, "error": "進階引擎未載入"}), 503
            
            data = request.get_json()
            result = self.advanced.analyze_feixing(
                source_gong=data.get("source_gong"),
                gong_gan=data.get("gong_gan"),
                star_positions=data.get("star_positions")
            )
            return jsonify(result)
        
        @self.app.route("/api/sihua/zihua", methods=["POST"])
        def api_zihua():
            """自化分析"""
            if not self.advanced:
                return jsonify({"success": False, "error": "進階引擎未載入"}), 503
            
            data = request.get_json()
            result = self.advanced.analyze_zihua(
                gong=data.get("gong"),
                gong_gan=data.get("gong_gan"),
                stars=data.get("stars", [])
            )
            return jsonify(result)
        
        @self.app.route("/api/qimen", methods=["POST"])
        def api_qimen():
            """奇門遁甲"""
            if not self.advanced:
                return jsonify({"success": False, "error": "進階引擎未載入"}), 503
            
            data = request.get_json() or {}
            dt = None
            if data.get("datetime"):
                dt = datetime.fromisoformat(data["datetime"])
            
            result = self.advanced.create_qimen(dt)
            return jsonify(result)
        
        @self.app.route("/api/liuren", methods=["POST"])
        def api_liuren():
            """六壬神課"""
            if not self.advanced:
                return jsonify({"success": False, "error": "進階引擎未載入"}), 503
            
            data = request.get_json()
            result = self.advanced.create_liuren(
                day_gan=data.get("day_gan"),
                day_zhi=data.get("day_zhi"),
                hour_zhi=data.get("hour_zhi"),
                is_day=data.get("is_day", True)
            )
            return jsonify(result)
        
        @self.app.route("/api/fengshui", methods=["POST"])
        def api_fengshui():
            """風水羅盤"""
            if not self.advanced:
                return jsonify({"success": False, "error": "進階引擎未載入"}), 503
            
            data = request.get_json()
            result = self.advanced.analyze_fengshui(
                degree=data.get("degree"),
                year=data.get("year")
            )
            return jsonify(result)
        
        # ===== 文檔端點 =====
        
        @self.app.route("/docs")
        def docs():
            """API 文檔"""
            endpoints = []
            
            for rule in self.app.url_map.iter_rules():
                if rule.endpoint != 'static':
                    methods = ','.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
                    tier = ENDPOINT_TIERS.get(str(rule), "free")
                    endpoints.append({
                        "path": str(rule),
                        "methods": methods,
                        "tier": tier
                    })
            
            return jsonify({
                "name": "北斗命數 API",
                "version": self.VERSION,
                "endpoints": sorted(endpoints, key=lambda x: x["path"])
            })
    
    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
        """啟動服務"""
        print(f"北斗命數 API v{self.VERSION} 啟動中...")
        print(f"訪問: http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


# =============================================================================
# CLI 入口
# =============================================================================

def main():
    """CLI 入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="北斗命數統一API v2.0")
    parser.add_argument("--serve", type=int, help="啟動服務，指定端口")
    parser.add_argument("--status", action="store_true", help="顯示系統狀態")
    args = parser.parse_args()
    
    if args.status:
        print("=" * 70)
        print("北斗命數 API v2.0 系統狀態")
        print("=" * 70)
        
        engines = {
            "核心引擎 (mingshu)": ENGINE_AVAILABLE,
            "流年合盤 (liunian)": LIUNIAN_AVAILABLE,
            "擇日存儲 (zeri)": ZERI_AVAILABLE,
            "姓名嫁娶 (naming)": NAMING_AVAILABLE,
            "梅花PDF (meihua)": MEIHUA_AVAILABLE,
            "進階術數 (advanced)": ADVANCED_AVAILABLE,
            "場論引擎 (field)": FIELD_AVAILABLE,
            "商用套件 (commercial)": COMMERCIAL_AVAILABLE,
        }
        
        print("\n【引擎狀態】")
        for name, available in engines.items():
            icon = "✓" if available else "○"
            print(f"  {icon} {name}")
        
        available = sum(engines.values())
        print(f"\n【總計】{available}/{len(engines)} 引擎可用")
        
        print("\n【端點統計】")
        basic_count = sum(1 for t in ENDPOINT_TIERS.values() if t == "basic")
        pro_count = sum(1 for t in ENDPOINT_TIERS.values() if t == "pro")
        adv_count = sum(1 for t in ENDPOINT_TIERS.values() if t == "advanced")
        print(f"  基本版: {basic_count} 端點")
        print(f"  專業版: {pro_count} 端點")
        print(f"  進階版: {adv_count} 端點")
        print(f"  總計: {len(ENDPOINT_TIERS)} 端點")
        
    elif args.serve:
        api = MingshuUnifiedAPIv2()
        api.run(port=args.serve)
    else:
        print("北斗命數 API v2.0")
        print("使用 --serve PORT 啟動服務")
        print("使用 --status 查看狀態")
        
        # 顯示簡要狀態
        api = MingshuUnifiedAPIv2()
        print(f"\n引擎狀態: {sum([ENGINE_AVAILABLE, LIUNIAN_AVAILABLE, ZERI_AVAILABLE, NAMING_AVAILABLE, MEIHUA_AVAILABLE, ADVANCED_AVAILABLE, FIELD_AVAILABLE, COMMERCIAL_AVAILABLE])}/8 可用")
        print(f"API 端點: {len(ENDPOINT_TIERS)} 個")


if __name__ == "__main__":
    main()
