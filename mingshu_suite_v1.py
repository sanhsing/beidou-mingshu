#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mingshu_suite_v1.py - 北斗命數整合套件 v1.0
=============================================
北斗七星文創 × 織明

XTF⁸ 任務鏈：M2+M3+M4
執行星：織明(設計) × 理樞(整合) × 澄書(記錄) × 流祇(連結)

模組整合：
    M2: ReportGenerator   - 命盤報告生成 (Markdown/HTML)
    M3: FieldAdvisor      - 場論×命數決策建議
    M4: MingshuAPI        - 統一REST API路由

依賴：
    - mingshu_engine_v1.py (統一命數引擎)
    - field_engine_v1.py (場論引擎)
    - PYLIB: doe_decision, wuxing_core

📚 知識點：
    「命數非裁決律」：術數之間不互相裁決
    「場態合成」：多術數 → 場論維度同構收斂
    「決策場論」：場態評估 → 最優行動
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any, Callable
from enum import Enum
from datetime import datetime, date
import json
import os

# 導入本地模組
try:
    from mingshu_engine_v1 import (
        MingshuEngine, MingshuResult, BirthInfo, BaziChart,
        ZiweiChart, GuaResult, FieldState, Gender, CalendarType
    )
except ImportError:
    pass

try:
    from field_engine_v1 import (
        FieldEngine, ContactState, RelationMode
    )
except ImportError:
    pass


# =============================================================================
# M2: 報告生成器 (ReportGenerator)
# =============================================================================

class ReportFormat(Enum):
    MARKDOWN = "md"
    HTML = "html"
    JSON = "json"
    TEXT = "txt"


@dataclass
class ReportConfig:
    """報告配置"""
    format: ReportFormat = ReportFormat.MARKDOWN
    include_bazi: bool = True
    include_ziwei: bool = True
    include_yijing: bool = True
    include_field: bool = True
    include_advice: bool = True
    lang: str = "zh-TW"
    style: str = "default"


class ReportGenerator:
    """
    命盤報告生成器
    
    M2: MingshuResult → 格式化報告
    
    📚 知識點：
        報告 = 命數可視化
        格式化 = 人機界面
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config: ReportConfig = None):
        self.config = config or ReportConfig()
    
    # -------------------------------------------------------------------------
    # Markdown 生成
    # -------------------------------------------------------------------------
    
    def to_markdown(self, result: MingshuResult) -> str:
        """生成 Markdown 報告"""
        lines = []
        
        # 標題
        name = result.birth_info.name or "命盤"
        lines.append(f"# {name} 命數報告")
        lines.append(f"\n*生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
        
        # 基本資訊
        lines.append("## 📋 基本資訊\n")
        bi = result.birth_info
        calendar_str = "農曆" if bi.calendar == CalendarType.LUNAR else "陽曆"
        gender_str = "男" if bi.gender == Gender.MALE else "女"
        lines.append(f"- **姓名**：{bi.name or '未提供'}")
        lines.append(f"- **生辰**：{calendar_str} {bi.year}年{bi.month}月{bi.day}日 {bi.hour}時")
        lines.append(f"- **性別**：{gender_str}")
        lines.append("")
        
        # 八字
        if self.config.include_bazi and result.bazi:
            lines.append("## 🔮 八字命盤\n")
            lines.append(f"**四柱**：{result.bazi.bazi_string}\n")
            lines.append(f"- **日主**：{result.bazi.day_master}")
            
            # 五行統計
            wx_count = result.bazi.get_wuxing_count()
            wx_str = " / ".join(f"{k}:{v}" for k, v in wx_count.items())
            lines.append(f"- **五行**：{wx_str}")
            
            # 分析
            if "bazi" in result.analysis:
                ba = result.analysis["bazi"]
                lines.append(f"- **格局**：{ba.get('pattern', '未判定')}")
                lines.append(f"- **身強弱**：{ba.get('strength', '未判定')}")
                lines.append(f"- **用神**：{ba.get('yongshen', '未判定')}")
            lines.append("")
        
        # 紫微
        if self.config.include_ziwei and result.ziwei:
            lines.append("## ⭐ 紫微斗數\n")
            lines.append(f"- **命宮位置**：第{result.ziwei.ming_gong}宮")
            lines.append(f"- **身宮位置**：第{result.ziwei.shen_gong}宮")
            
            # 命宮星曜
            ming_palace = result.ziwei.get_palace("命宮")
            if ming_palace:
                if ming_palace.main_stars:
                    lines.append(f"- **命宮主星**：{', '.join(ming_palace.main_stars)}")
                if ming_palace.sihua:
                    lines.append(f"- **命宮四化**：{', '.join(ming_palace.sihua)}")
            lines.append("")
        
        # 易經
        if self.config.include_yijing and result.yijing:
            lines.append("## ☯ 易經本命卦\n")
            lines.append(f"- **本卦**：{result.yijing.ben_gua}")
            if result.yijing.dong_yao:
                lines.append(f"- **動爻**：第{result.yijing.dong_yao}爻")
            if result.yijing.has_bian:
                lines.append(f"- **變卦**：{result.yijing.bian_gua}")
            lines.append("")
        
        # 場態
        if self.config.include_field and result.field_state:
            lines.append("## 🌊 場態分析\n")
            fs = result.field_state
            lines.append(f"**場態總分**：{fs.field_score:.1f}/100\n")
            lines.append("| 維度 | 數值 | 說明 |")
            lines.append("|:-----|-----:|:-----|")
            lines.append(f"| 共振度 | {fs.coherence:.2f} | 場的攻擊性/主動性 |")
            lines.append(f"| 摩擦度 | {fs.friction:.2f} | 場的阻力/邊界弱度 |")
            lines.append(f"| 波動度 | {fs.volatility:.2f} | 場的不穩定性 |")
            lines.append(f"| 持續度 | {fs.sustainability:.2f} | 場的持久力 |")
            lines.append("")
            
            if fs.triggers:
                lines.append(f"**觸發點**：{', '.join(fs.triggers)}")
                lines.append("")
        
        # 建議
        if self.config.include_advice and result.advice:
            lines.append("## 💡 建議\n")
            for adv in result.advice:
                lines.append(f"- {adv}")
            lines.append("")
        
        # 聲明
        lines.append("---")
        lines.append("*本報告由北斗命數引擎生成，僅供參考。*")
        lines.append("*命數非裁決律：術數之間不互相裁決。*")
        
        return "\n".join(lines)
    
    # -------------------------------------------------------------------------
    # HTML 生成
    # -------------------------------------------------------------------------
    
    def to_html(self, result: MingshuResult) -> str:
        """生成 HTML 報告"""
        md_content = self.to_markdown(result)
        
        # 簡易 Markdown → HTML 轉換
        html_content = self._md_to_html(md_content)
        
        template = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{result.birth_info.name or '命盤'} 命數報告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Microsoft JhengHei', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background: #f8f9fa; }}
        ul {{ padding-left: 20px; }}
        li {{ margin: 8px 0; }}
        .field-score {{
            font-size: 2em;
            color: #3498db;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>"""
        return template
    
    def _md_to_html(self, md: str) -> str:
        """簡易 Markdown → HTML"""
        import re
        
        # Headers
        md = re.sub(r'^# (.+)$', r'<h1>\1</h1>', md, flags=re.MULTILINE)
        md = re.sub(r'^## (.+)$', r'<h2>\1</h2>', md, flags=re.MULTILINE)
        md = re.sub(r'^### (.+)$', r'<h3>\1</h3>', md, flags=re.MULTILINE)
        
        # Bold
        md = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', md)
        
        # Italic
        md = re.sub(r'\*(.+?)\*', r'<em>\1</em>', md)
        
        # Lists
        lines = md.split('\n')
        in_list = False
        result = []
        for line in lines:
            if line.startswith('- '):
                if not in_list:
                    result.append('<ul>')
                    in_list = True
                result.append(f'<li>{line[2:]}</li>')
            else:
                if in_list:
                    result.append('</ul>')
                    in_list = False
                result.append(line)
        if in_list:
            result.append('</ul>')
        
        # Tables (簡化處理)
        html = '\n'.join(result)
        html = re.sub(r'^\|(.+)\|$', r'<tr><td>\1</td></tr>', html, flags=re.MULTILINE)
        html = html.replace('|', '</td><td>')
        
        # Paragraphs
        html = re.sub(r'\n\n', '</p><p>', html)
        
        return f'<p>{html}</p>'
    
    # -------------------------------------------------------------------------
    # JSON 生成
    # -------------------------------------------------------------------------
    
    def to_json(self, result: MingshuResult, pretty: bool = True) -> str:
        """生成 JSON 報告"""
        data = result.to_dict()
        data["_meta"] = {
            "version": self.VERSION,
            "generated_at": datetime.now().isoformat(),
            "format": "json"
        }
        if pretty:
            return json.dumps(data, ensure_ascii=False, indent=2)
        return json.dumps(data, ensure_ascii=False)
    
    # -------------------------------------------------------------------------
    # 統一生成
    # -------------------------------------------------------------------------
    
    def generate(
        self,
        result: MingshuResult,
        format: ReportFormat = None
    ) -> str:
        """生成報告"""
        fmt = format or self.config.format
        
        if fmt == ReportFormat.MARKDOWN:
            return self.to_markdown(result)
        elif fmt == ReportFormat.HTML:
            return self.to_html(result)
        elif fmt == ReportFormat.JSON:
            return self.to_json(result)
        else:
            return self.to_markdown(result)
    
    def save(
        self,
        result: MingshuResult,
        filepath: str,
        format: ReportFormat = None
    ) -> str:
        """保存報告到檔案"""
        content = self.generate(result, format)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath


# =============================================================================
# M3: 場論決策顧問 (FieldAdvisor)
# =============================================================================

@dataclass
class DecisionContext:
    """決策情境"""
    question: str                   # 決策問題
    options: List[str] = None       # 選項列表
    domain: str = "general"         # 領域 (career/relationship/health/wealth)
    urgency: float = 0.5            # 緊迫度 [0, 1]
    reversibility: float = 0.5      # 可逆度 [0, 1]


@dataclass
class DecisionAdvice:
    """決策建議"""
    recommendation: str             # 建議
    confidence: float              # 信心度 [0, 1]
    field_alignment: float         # 場態對齊度
    timing_advice: str             # 時機建議
    risk_factors: List[str]        # 風險因素
    supporting_evidence: List[str]  # 支持證據
    
    def to_dict(self) -> Dict:
        return {
            "recommendation": self.recommendation,
            "confidence": round(self.confidence, 3),
            "field_alignment": round(self.field_alignment, 3),
            "timing_advice": self.timing_advice,
            "risk_factors": self.risk_factors,
            "supporting_evidence": self.supporting_evidence
        }


class FieldAdvisor:
    """
    場論決策顧問
    
    M3: MingshuResult + FieldState → DecisionAdvice
    
    📚 知識點：
        決策 = 場態評估
        最優選擇 = argmax(場強)
        場不逆操 = 順勢而為
    """
    
    VERSION = "1.0.0"
    
    # 領域權重
    DOMAIN_WEIGHTS = {
        "career": {"coherence": 0.4, "sustainability": 0.3, "friction": 0.2, "volatility": 0.1},
        "relationship": {"coherence": 0.3, "friction": 0.35, "volatility": 0.2, "sustainability": 0.15},
        "health": {"sustainability": 0.5, "volatility": 0.25, "friction": 0.15, "coherence": 0.1},
        "wealth": {"coherence": 0.35, "sustainability": 0.35, "volatility": 0.2, "friction": 0.1},
        "general": {"coherence": 0.25, "friction": 0.25, "volatility": 0.25, "sustainability": 0.25}
    }
    
    def __init__(self):
        pass
    
    def analyze(
        self,
        mingshu: MingshuResult,
        context: DecisionContext
    ) -> DecisionAdvice:
        """
        場論決策分析
        
        📚 知識點：
            1. 場態評估 → 基礎判斷
            2. 領域權重 → 調整分數
            3. 時機判斷 → 行動建議
        """
        field = mingshu.field_state
        if not field:
            return DecisionAdvice(
                recommendation="場態資訊不足，建議補充命盤分析",
                confidence=0.1,
                field_alignment=0.0,
                timing_advice="未知",
                risk_factors=["場態未計算"],
                supporting_evidence=[]
            )
        
        # 1. 計算領域加權分數
        weights = self.DOMAIN_WEIGHTS.get(context.domain, self.DOMAIN_WEIGHTS["general"])
        
        weighted_score = (
            field.coherence * weights["coherence"] +
            (1 - field.friction) * weights["friction"] +
            (1 - field.volatility) * weights["volatility"] +
            field.sustainability * weights["sustainability"]
        )
        
        # 正規化到 [0, 1]
        field_alignment = (weighted_score + 1) / 2
        
        # 2. 時機判斷
        timing_advice = self._evaluate_timing(field, context)
        
        # 3. 風險分析
        risk_factors = self._identify_risks(field, mingshu)
        
        # 4. 生成建議
        recommendation = self._generate_recommendation(
            field, field_alignment, context, timing_advice
        )
        
        # 5. 支持證據
        evidence = self._collect_evidence(mingshu)
        
        # 6. 信心度計算
        confidence = self._calculate_confidence(
            field_alignment, len(risk_factors), context.reversibility
        )
        
        return DecisionAdvice(
            recommendation=recommendation,
            confidence=confidence,
            field_alignment=field_alignment,
            timing_advice=timing_advice,
            risk_factors=risk_factors,
            supporting_evidence=evidence
        )
    
    def _evaluate_timing(self, field: FieldState, context: DecisionContext) -> str:
        """時機評估"""
        # 波動度高 → 宜靜待
        if field.volatility > 0.7:
            return "場態波動大，建議靜待時機"
        
        # 共振度高 + 摩擦度低 → 可積極
        if field.coherence > 0.3 and field.friction < 0.3:
            return "場態良好，可積極行動"
        
        # 持續度高 → 適合長期
        if field.sustainability > 0.7:
            return "場態穩定，適合長期規劃"
        
        # 緊迫度高 + 場態中性 → 速戰速決
        if context.urgency > 0.7:
            return "事態緊迫，建議速戰速決"
        
        return "場態中性，穩健推進"
    
    def _identify_risks(self, field: FieldState, mingshu: MingshuResult) -> List[str]:
        """識別風險因素"""
        risks = []
        
        # 場態風險
        if field.volatility > 0.6:
            risks.append("場態不穩定，變數較多")
        if field.friction > 0.5:
            risks.append("阻力較大，需額外努力")
        if field.coherence < -0.3:
            risks.append("場態負向，不利主動出擊")
        if field.sustainability < 0.3:
            risks.append("持續力弱，難以持久")
        
        # 命盤風險
        if mingshu.bazi:
            wx = mingshu.bazi.get_wuxing_count()
            missing = [k for k, v in wx.items() if v == 0]
            if missing:
                risks.append(f"五行缺{'/'.join(missing)}，注意相關領域")
        
        return risks
    
    def _generate_recommendation(
        self,
        field: FieldState,
        alignment: float,
        context: DecisionContext,
        timing: str
    ) -> str:
        """生成建議"""
        # 基於場態對齊度
        if alignment > 0.7:
            base = "場態有利，可積極推進"
        elif alignment > 0.5:
            base = "場態中性，穩健行動"
        elif alignment > 0.3:
            base = "場態欠佳，謹慎評估"
        else:
            base = "場態不利，建議暫緩或調整方向"
        
        # 根據領域調整
        domain_tips = {
            "career": "事業決策需考慮長期發展",
            "relationship": "關係決策需顧及雙方場態",
            "health": "健康決策以穩定為先",
            "wealth": "財務決策需風險對沖"
        }
        
        tip = domain_tips.get(context.domain, "")
        
        if context.options:
            return f"{base}。{tip}。建議從「{context.options[0]}」等選項中，選擇最順勢者。"
        
        return f"{base}。{tip}"
    
    def _collect_evidence(self, mingshu: MingshuResult) -> List[str]:
        """收集支持證據"""
        evidence = []
        
        if mingshu.bazi:
            evidence.append(f"八字日主：{mingshu.bazi.day_master}")
            if "bazi" in mingshu.analysis:
                ba = mingshu.analysis["bazi"]
                evidence.append(f"身強弱：{ba.get('strength', '未知')}")
        
        if mingshu.yijing:
            evidence.append(f"本命卦：{mingshu.yijing.ben_gua}")
            if mingshu.yijing.has_bian:
                evidence.append(f"變卦：{mingshu.yijing.bian_gua}")
        
        if mingshu.field_state:
            evidence.append(f"場態分：{mingshu.field_state.field_score:.1f}/100")
        
        return evidence
    
    def _calculate_confidence(
        self,
        alignment: float,
        risk_count: int,
        reversibility: float
    ) -> float:
        """計算信心度"""
        # 基礎信心 = 對齊度
        base = alignment
        
        # 風險懲罰
        risk_penalty = risk_count * 0.1
        
        # 可逆度加成
        reversibility_bonus = reversibility * 0.1
        
        confidence = base - risk_penalty + reversibility_bonus
        return max(0.1, min(0.95, confidence))
    
    def quick_advice(self, mingshu: MingshuResult, question: str) -> str:
        """快速建議"""
        context = DecisionContext(question=question)
        advice = self.analyze(mingshu, context)
        return f"{advice.recommendation} (信心度：{advice.confidence:.0%}，{advice.timing_advice})"


# =============================================================================
# M4: 統一 API 路由 (MingshuAPI)
# =============================================================================

@dataclass
class APIRequest:
    """API 請求"""
    endpoint: str
    method: str = "POST"
    params: Dict = field(default_factory=dict)
    body: Dict = field(default_factory=dict)


@dataclass
class APIResponse:
    """API 響應"""
    success: bool
    data: Any = None
    error: str = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class MingshuAPI:
    """
    統一命數 API 路由
    
    M4: HTTP Request → JSON Response
    
    📚 知識點：
        API = 人機接口
        路由 = 功能分發
        RESTful = 資源導向
    
    端點：
        POST /bazi          - 八字排盤
        POST /ziwei         - 紫微排盤
        POST /yijing        - 易經起卦
        POST /full          - 完整命盤
        POST /field         - 場態分析
        POST /advice        - 決策建議
        POST /report        - 生成報告
        GET  /health        - 健康檢查
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.engine = MingshuEngine()
        self.report_gen = ReportGenerator()
        self.field_advisor = FieldAdvisor()
        
        # 路由表
        self.routes = {
            "bazi": self._handle_bazi,
            "ziwei": self._handle_ziwei,
            "yijing": self._handle_yijing,
            "full": self._handle_full,
            "field": self._handle_field,
            "advice": self._handle_advice,
            "report": self._handle_report,
            "health": self._handle_health,
            "now": self._handle_now,
            "liunian": self._handle_liunian,
            "hepan": self._handle_hepan,
            "zeri": self._handle_zeri,
        }
    
    def handle(self, request: APIRequest) -> APIResponse:
        """處理 API 請求"""
        endpoint = request.endpoint.strip("/").lower()
        
        handler = self.routes.get(endpoint)
        if not handler:
            return APIResponse(
                success=False,
                error=f"Unknown endpoint: {endpoint}"
            )
        
        try:
            data = handler(request)
            return APIResponse(success=True, data=data)
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def _parse_birth_info(self, body: Dict) -> BirthInfo:
        """解析出生資訊"""
        return BirthInfo(
            year=body.get("year", 1990),
            month=body.get("month", 1),
            day=body.get("day", 1),
            hour=body.get("hour", 12),
            minute=body.get("minute", 0),
            gender=Gender(body.get("gender", "M")),
            calendar=CalendarType(body.get("calendar", "lunar")),
            name=body.get("name", "")
        )
    
    # -------------------------------------------------------------------------
    # 路由處理器
    # -------------------------------------------------------------------------
    
    def _handle_bazi(self, req: APIRequest) -> Dict:
        """八字排盤"""
        birth = self._parse_birth_info(req.body)
        chart = self.engine.get_bazi(birth)
        analysis = self.engine.analyze_bazi(chart)
        return {
            "chart": chart.to_dict(),
            "analysis": analysis
        }
    
    def _handle_ziwei(self, req: APIRequest) -> Dict:
        """紫微排盤"""
        birth = self._parse_birth_info(req.body)
        chart = self.engine.get_ziwei(birth)
        return chart.to_dict()
    
    def _handle_yijing(self, req: APIRequest) -> Dict:
        """易經起卦"""
        method = req.body.get("method", "birthday")
        
        if method == "birthday":
            birth = self._parse_birth_info(req.body)
            gua = self.engine.get_yijing(birth)
        else:
            gua = self.engine.get_yijing_now()
        
        return gua.to_dict()
    
    def _handle_full(self, req: APIRequest) -> Dict:
        """完整命盤"""
        birth = self._parse_birth_info(req.body)
        result = self.engine.generate_full(birth)
        return result.to_dict()
    
    def _handle_field(self, req: APIRequest) -> Dict:
        """場態分析"""
        birth = self._parse_birth_info(req.body)
        result = self.engine.generate_full(birth)
        
        if result.field_state:
            return result.field_state.to_dict()
        return {"error": "場態計算失敗"}
    
    def _handle_advice(self, req: APIRequest) -> Dict:
        """決策建議"""
        birth = self._parse_birth_info(req.body)
        result = self.engine.generate_full(birth)
        
        context = DecisionContext(
            question=req.body.get("question", ""),
            options=req.body.get("options", []),
            domain=req.body.get("domain", "general"),
            urgency=req.body.get("urgency", 0.5),
            reversibility=req.body.get("reversibility", 0.5)
        )
        
        advice = self.field_advisor.analyze(result, context)
        return advice.to_dict()
    
    def _handle_report(self, req: APIRequest) -> Dict:
        """生成報告"""
        birth = self._parse_birth_info(req.body)
        result = self.engine.generate_full(birth)
        
        format_str = req.body.get("format", "markdown")
        format_map = {
            "markdown": ReportFormat.MARKDOWN,
            "md": ReportFormat.MARKDOWN,
            "html": ReportFormat.HTML,
            "json": ReportFormat.JSON
        }
        
        fmt = format_map.get(format_str, ReportFormat.MARKDOWN)
        content = self.report_gen.generate(result, fmt)
        
        return {
            "format": fmt.value,
            "content": content
        }
    
    def _handle_health(self, req: APIRequest) -> Dict:
        """健康檢查"""
        return {
            "status": "healthy",
            "version": self.VERSION,
            "engine_version": self.engine.VERSION,
            "endpoints": list(self.routes.keys())
        }
    
    def _handle_now(self, req: APIRequest) -> Dict:
        """當下起卦"""
        gua = self.engine.get_yijing_now()
        return gua.to_dict()
    
    def _handle_liunian(self, req: APIRequest) -> Dict:
        """M5: 流年運勢"""
        try:
            from mingshu_liunian_hepan_v1 import LiunianEngine
            from datetime import date
            
            liunian = LiunianEngine()
            birth = self._parse_birth_info(req.body)
            
            # 解析目標日期
            target_str = req.body.get("target_date")
            if target_str:
                target = date.fromisoformat(target_str)
            else:
                target = date.today()
            
            result = liunian.analyze(birth, target)
            return result.to_dict()
        except ImportError:
            return {"error": "LiunianEngine not available"}
    
    def _handle_hepan(self, req: APIRequest) -> Dict:
        """M6: 人際合盤"""
        try:
            from mingshu_liunian_hepan_v1 import HepanEngine
            
            hepan = HepanEngine()
            
            # 解析兩人資訊
            person_a_data = req.body.get("person_a", req.body)
            person_b_data = req.body.get("person_b", {})
            
            if not person_b_data:
                return {"error": "person_b is required"}
            
            person_a = self._parse_birth_info(person_a_data)
            person_b = self._parse_birth_info(person_b_data)
            
            result = hepan.analyze(person_a, person_b)
            return result.to_dict()
        except ImportError:
            return {"error": "HepanEngine not available"}
    
    def _handle_zeri(self, req: APIRequest) -> Dict:
        """M7: 擇日擇時"""
        try:
            from mingshu_zeri_db_web_v1 import ZeriEngine, ActivityType
            
            zeri = ZeriEngine()
            birth = self._parse_birth_info(req.body)
            
            # 解析活動類型
            activity_str = req.body.get("activity", "general")
            try:
                activity = ActivityType(activity_str)
            except:
                activity = ActivityType.GENERAL
            
            days = req.body.get("days", 7)
            result = zeri.analyze(birth, activity, days=days)
            return result.to_dict()
        except ImportError:
            return {"error": "ZeriEngine not available"}


# =============================================================================
# CLI 入口
# =============================================================================

def main():
    """CLI 入口"""
    print("=" * 60)
    print("北斗命數整合套件 v1.0")
    print("M2 (報告) + M3 (場論決策) + M4 (API)")
    print("=" * 60)
    
    # 初始化
    engine = MingshuEngine()
    report_gen = ReportGenerator()
    advisor = FieldAdvisor()
    api = MingshuAPI()
    
    # 測試命盤
    birth = BirthInfo(
        year=1983, month=12, day=16, hour=5,
        gender=Gender.MALE, calendar=CalendarType.LUNAR, name="北斗"
    )
    
    result = engine.generate_full(birth)
    
    # M2: 報告生成
    print("\n【M2 報告生成】")
    md_report = report_gen.to_markdown(result)
    print(f"  Markdown 報告長度: {len(md_report)} 字符")
    print(f"  前200字:\n{md_report[:200]}...")
    
    # M3: 場論決策
    print("\n【M3 場論決策】")
    context = DecisionContext(
        question="是否適合今年創業？",
        domain="career",
        urgency=0.6
    )
    advice = advisor.analyze(result, context)
    print(f"  建議: {advice.recommendation}")
    print(f"  信心度: {advice.confidence:.1%}")
    print(f"  時機: {advice.timing_advice}")
    
    # M4: API 測試
    print("\n【M4 API測試】")
    
    # 健康檢查
    req = APIRequest(endpoint="/health")
    resp = api.handle(req)
    print(f"  /health: {resp.data}")
    
    # 八字排盤
    req = APIRequest(endpoint="/bazi", body=birth.to_dict())
    resp = api.handle(req)
    print(f"  /bazi: 八字 = {resp.data['chart']['bazi_string']}")
    
    # 當下起卦
    req = APIRequest(endpoint="/now")
    resp = api.handle(req)
    print(f"  /now: 本卦 = {resp.data['ben_gua']}")
    
    print("\n" + "=" * 60)
    print("M2+M3+M4 整合完成")
    print("=" * 60)


if __name__ == "__main__":
    main()


# =============================================================================
# 📚 知識點總結
# =============================================================================
"""
【M2+M3+M4 整合架構】

M2: ReportGenerator
├── to_markdown()  → Markdown 報告
├── to_html()      → HTML 報告
├── to_json()      → JSON 報告
└── save()         → 保存檔案

M3: FieldAdvisor
├── analyze()      → 場論決策分析
│   ├── 領域權重計算
│   ├── 時機評估
│   ├── 風險識別
│   └── 建議生成
└── quick_advice() → 快速建議

M4: MingshuAPI
├── /bazi          → 八字排盤
├── /ziwei         → 紫微排盤
├── /yijing        → 易經起卦
├── /full          → 完整命盤
├── /field         → 場態分析
├── /advice        → 決策建議
├── /report        → 生成報告
├── /now           → 當下起卦
└── /health        → 健康檢查

【核心原則】

1. 場論決策
   - 決策 = 場態評估
   - 最優選擇 = argmax(場強)
   - 場不逆操 = 順勢而為

2. 領域權重
   - career: coherence > sustainability
   - relationship: friction > coherence
   - health: sustainability > all
   - wealth: coherence ≈ sustainability

3. API 設計
   - RESTful 風格
   - JSON 輸入輸出
   - 統一錯誤處理

【織明語錄】
   - 「決策是場態的投影」
   - 「順勢而為，場不逆操」
   - 「API是人機的橋樑」
"""
