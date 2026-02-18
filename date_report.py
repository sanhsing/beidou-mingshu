#!/usr/bin/env python3
"""
date_report.py - 擇日報告生成器
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
功能：
  • 嫁娶擇日報告
  • 動土擇日報告
  • 多用途擇日報告
  • 支援 Markdown/HTML/PDF 輸出
═══════════════════════════════════════════════════════════════════════

XTF Task Chain: A
@11星協作：@織明(統籌) @璃語(樣式) @澄書(文檔)
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import date, datetime
import os

# 導入擇日模組
from date_base import get_ganzhi_from_date, get_full_rike, get_lunar_info, SHENGXIAO, DIZHI
from marry_date import MarryDateSelector, MarryCandidate
from ground_date import GroundDateSelector, GroundCandidate
from event_date import EventDateSelector, EventType, EventCandidate

# ════════════════════════════════════════════════════════════════════
# L0: 報告樣式
# ════════════════════════════════════════════════════════════════════

REPORT_CSS = """
<style>
    body { font-family: 'Noto Sans TC', 'Microsoft JhengHei', sans-serif; 
           max-width: 800px; margin: 0 auto; padding: 20px; 
           background: #f5f5f5; color: #333; }
    .header { text-align: center; padding: 30px; 
              background: linear-gradient(135deg, #1a1a2e, #302b63);
              color: #fff; border-radius: 15px; margin-bottom: 30px; }
    .header h1 { margin: 0; font-size: 2em; 
                 background: linear-gradient(90deg, #ffd700, #ff6b6b);
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .header p { margin: 10px 0 0; opacity: 0.8; }
    .info-box { background: #fff; padding: 20px; border-radius: 10px;
                margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .info-box h2 { color: #302b63; border-bottom: 2px solid #ffd700; 
                   padding-bottom: 10px; margin-top: 0; }
    .info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
    .info-item { background: #f8f9fa; padding: 12px; border-radius: 8px; }
    .info-item label { color: #666; font-size: 0.9em; display: block; }
    .info-item span { font-size: 1.1em; font-weight: bold; color: #333; }
    .result-card { background: #fff; padding: 25px; border-radius: 12px;
                   margin-bottom: 20px; box-shadow: 0 2px 15px rgba(0,0,0,0.1);
                   border-left: 5px solid #ffd700; }
    .result-header { display: flex; justify-content: space-between; 
                     align-items: center; margin-bottom: 20px; }
    .result-date { font-size: 1.4em; font-weight: bold; color: #302b63; }
    .result-score { background: linear-gradient(90deg, #ffd700, #ff6b6b);
                    color: #000; padding: 8px 20px; border-radius: 20px;
                    font-weight: bold; }
    .rike-box { background: linear-gradient(135deg, #302b63, #1a1a2e);
                color: #fff; padding: 20px; border-radius: 10px;
                text-align: center; margin-bottom: 20px; }
    .rike-box .label { opacity: 0.7; font-size: 0.9em; }
    .rike-box .value { font-size: 1.8em; font-family: monospace; 
                       letter-spacing: 3px; margin-top: 5px; }
    .detail-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
    .detail-item { background: #f8f9fa; padding: 10px; border-radius: 6px;
                   text-align: center; }
    .detail-item .label { color: #666; font-size: 0.8em; }
    .detail-item .value { font-weight: bold; color: #333; }
    .tag-list { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 15px; }
    .tag { padding: 5px 12px; border-radius: 15px; font-size: 0.85em; }
    .tag.good { background: #d4edda; color: #155724; }
    .tag.bad { background: #f8d7da; color: #721c24; }
    .tag.neutral { background: #e2e3e5; color: #383d41; }
    .jishi-list { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }
    .jishi-item { background: #e8f5e9; color: #2e7d32; padding: 8px 15px;
                  border-radius: 8px; font-family: monospace; }
    .footer { text-align: center; padding: 20px; color: #666; font-size: 0.9em; }
    @media print { body { background: #fff; } }
</style>
"""

# ════════════════════════════════════════════════════════════════════
# L1: 報告資料結構
# ════════════════════════════════════════════════════════════════════

@dataclass
class DateReportData:
    """擇日報告資料"""
    report_type: str  # marry/ground/event
    generated_at: str
    query_range: str
    
    # 查詢條件
    params: Dict[str, Any]
    
    # 結果
    results: List[Dict[str, Any]]
    
    # 備註
    notes: List[str] = None


# ════════════════════════════════════════════════════════════════════
# L2: 報告生成器
# ════════════════════════════════════════════════════════════════════

class DateReportGenerator:
    """擇日報告生成器"""
    
    def __init__(self):
        self.data: Optional[DateReportData] = None
    
    # ─────────────────────────────────────────────────────────────
    # 嫁娶報告
    # ─────────────────────────────────────────────────────────────
    
    def generate_marry_report(self, man_year: int, woman_year: int,
                               start: date, end: date, top_n: int = 5) -> DateReportData:
        """生成嫁娶擇日報告"""
        man_zhi = DIZHI[(man_year - 4) % 12]
        woman_zhi = DIZHI[(woman_year - 4) % 12]
        man_sx = SHENGXIAO[DIZHI.index(man_zhi)]
        woman_sx = SHENGXIAO[DIZHI.index(woman_zhi)]
        
        selector = MarryDateSelector(man_zhi, woman_zhi)
        candidates = selector.select_dates(start, end, top_n)
        
        results = []
        for c in candidates:
            rike = c.full_rike
            results.append({
                "date": str(c.date),
                "weekday": ["一", "二", "三", "四", "五", "六", "日"][c.date.weekday()],
                "ganzhi": c.ganzhi,
                "lunar": c.lunar,
                "full_rike": rike.full_rike if rike else "",
                "best_hour": rike.hour_gz if rike else "",
                "hour_score": rike.hour_score if rike else 0,
                "huangdao": c.huangdao_shen,
                "jianchu": c.jianchu,
                "xiu": c.xiu,
                "chong_sha": f"沖{c.chong_sx}煞{c.sha_fang}",
                "score": c.score.weighted_total,
                "is_dali": c.is_dali_yue,
                "is_xiaoli": c.is_xiaoli_yue,
                "ji_shen": c.marry_ji_shen,
                "xiong_shen": c.marry_xiong_shen,
                "jishi": [gz for _, gz, _ in (rike.jishi_list if rike else [])[:4]],
            })
        
        self.data = DateReportData(
            report_type="marry",
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            query_range=f"{start} ~ {end}",
            params={
                "man_year": man_year,
                "woman_year": woman_year,
                "man_sx": man_sx,
                "woman_sx": woman_sx,
                "man_zhi": man_zhi,
                "woman_zhi": woman_zhi,
                "dali_yue": selector.dali_yue,
                "xiaoli_yue": selector.xiaoli_yue,
            },
            results=results,
            notes=[
                "★ 大利月為最佳選擇，○ 小利月次之",
                "完整日課為年月日時四柱，擇吉時可提升效果",
                "本報告僅供參考，重大決策請諮詢專業命理師",
            ]
        )
        
        return self.data
    
    # ─────────────────────────────────────────────────────────────
    # 動土報告
    # ─────────────────────────────────────────────────────────────
    
    def generate_ground_report(self, owner_year: int, start: date, end: date,
                                zuoxiang: str = None, top_n: int = 5) -> DateReportData:
        """生成動土擇日報告"""
        owner_zhi = DIZHI[(owner_year - 4) % 12]
        owner_sx = SHENGXIAO[DIZHI.index(owner_zhi)]
        
        selector = GroundDateSelector(owner_zhi, zuoxiang=zuoxiang)
        candidates = selector.select_dates(start, end, top_n)
        
        results = []
        for c in candidates:
            rike = c.full_rike
            warnings = []
            if c.is_tuwang: warnings.append("土王用事")
            if c.is_tianhuo: warnings.append("天火")
            if c.is_dihuo: warnings.append("地火")
            if c.chong_owner: warnings.append("沖屋主")
            
            results.append({
                "date": str(c.date),
                "weekday": ["一", "二", "三", "四", "五", "六", "日"][c.date.weekday()],
                "ganzhi": c.ganzhi,
                "lunar": c.lunar,
                "full_rike": rike.full_rike if rike else "",
                "best_hour": rike.hour_gz if rike else "",
                "hour_score": rike.hour_score if rike else 0,
                "huangdao": c.huangdao_shen,
                "jianchu": c.jianchu,
                "xiu": c.xiu,
                "chong_sha": f"沖{c.chong_sx}煞{c.sha_fang}",
                "score": c.score.weighted_total,
                "ji_shen": c.ground_ji_shen,
                "xiong_shen": c.ground_xiong_shen,
                "warnings": warnings,
                "jishi": [gz for _, gz, _ in (rike.jishi_list if rike else [])[:4]],
            })
        
        self.data = DateReportData(
            report_type="ground",
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            query_range=f"{start} ~ {end}",
            params={
                "owner_year": owner_year,
                "owner_sx": owner_sx,
                "owner_zhi": owner_zhi,
                "zuoxiang": zuoxiang,
            },
            results=results,
            notes=[
                "動土吉日需避開土王用事、天火、地火等凶煞",
                "坐向煞方需特別注意，建議諮詢風水師",
                "完整日課四柱可作為擇時參考",
            ]
        )
        
        return self.data
    
    # ─────────────────────────────────────────────────────────────
    # 多用途報告
    # ─────────────────────────────────────────────────────────────
    
    def generate_event_report(self, event_type: str, start: date, end: date,
                               owner_year: int = None, top_n: int = 5) -> DateReportData:
        """生成多用途擇日報告"""
        event_map = {
            "開市": EventType.KAISHI,
            "搬家": EventType.BANJIA,
            "安床": EventType.ANCHUANG,
            "祭祀": EventType.JISI,
            "出行": EventType.CHUXING,
        }
        etype = event_map.get(event_type)
        if not etype:
            raise ValueError(f"不支援的類型：{event_type}")
        
        owner_zhi = DIZHI[(owner_year - 4) % 12] if owner_year else None
        owner_sx = SHENGXIAO[DIZHI.index(owner_zhi)] if owner_zhi else None
        
        selector = EventDateSelector(etype, owner_zhi)
        candidates = selector.select_dates(start, end, top_n)
        
        results = []
        for c in candidates:
            rike = c.full_rike
            results.append({
                "date": str(c.date),
                "weekday": ["一", "二", "三", "四", "五", "六", "日"][c.date.weekday()],
                "ganzhi": c.ganzhi,
                "lunar": c.lunar,
                "full_rike": rike.full_rike if rike else "",
                "best_hour": rike.hour_gz if rike else "",
                "hour_score": rike.hour_score if rike else 0,
                "huangdao": c.huangdao_shen,
                "jianchu": c.jianchu,
                "xiu": c.xiu,
                "chong_sha": f"沖{c.chong_sx}煞{c.sha_fang}",
                "score": c.score.weighted_total,
                "ji_shen": c.event_ji_shen,
                "xiong_shen": c.event_xiong_shen,
                "jishi": [gz for _, gz, _ in (rike.jishi_list if rike else [])[:4]],
            })
        
        self.data = DateReportData(
            report_type="event",
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            query_range=f"{start} ~ {end}",
            params={
                "event_type": event_type,
                "owner_year": owner_year,
                "owner_sx": owner_sx,
            },
            results=results,
            notes=[
                f"本報告為「{event_type}」用途擇日",
                "選擇黃道吉日、建除宜日可提升吉利程度",
                "如有個人八字資料，可進一步配合分析",
            ]
        )
        
        return self.data
    
    # ─────────────────────────────────────────────────────────────
    # 輸出格式
    # ─────────────────────────────────────────────────────────────
    
    def to_markdown(self) -> str:
        """輸出 Markdown 格式"""
        if not self.data:
            return ""
        
        d = self.data
        lines = []
        
        # 標題
        type_names = {"marry": "嫁娶擇日", "ground": "動土擇日", "event": d.params.get("event_type", "擇日")}
        lines.append(f"# 📅 {type_names.get(d.report_type, '擇日')}報告\n")
        lines.append(f"生成時間：{d.generated_at}\n")
        lines.append(f"查詢範圍：{d.query_range}\n")
        
        # 查詢條件
        lines.append("\n## 📋 查詢條件\n")
        if d.report_type == "marry":
            lines.append(f"- 男方：{d.params['man_year']}年（{d.params['man_sx']}）")
            lines.append(f"- 女方：{d.params['woman_year']}年（{d.params['woman_sx']}）")
            lines.append(f"- 大利月：{d.params['dali_yue']}")
            lines.append(f"- 小利月：{d.params['xiaoli_yue']}")
        elif d.report_type == "ground":
            lines.append(f"- 屋主：{d.params['owner_year']}年（{d.params['owner_sx']}）")
            if d.params.get('zuoxiang'):
                lines.append(f"- 坐向：{d.params['zuoxiang']}")
        else:
            lines.append(f"- 用途：{d.params.get('event_type', '擇日')}")
            if d.params.get('owner_sx'):
                lines.append(f"- 事主：{d.params['owner_year']}年（{d.params['owner_sx']}）")
        
        # 結果
        lines.append("\n## 🏆 推薦吉日\n")
        for i, r in enumerate(d.results, 1):
            mark = ""
            if d.report_type == "marry":
                if r.get("is_dali"): mark = " ★大利"
                elif r.get("is_xiaoli"): mark = " ○小利"
            
            lines.append(f"### #{i} {r['date']}（週{r['weekday']}）{r['ganzhi']}{mark}\n")
            lines.append(f"**完整日課**：`{r['full_rike']}`\n")
            lines.append(f"- 農曆：{r['lunar']}")
            lines.append(f"- 黃道：{r['huangdao']} | 建除：{r['jianchu']} | 二十八宿：{r['xiu']}")
            lines.append(f"- {r['chong_sha']}")
            lines.append(f"- **評分：{r['score']:.0f} 分**")
            
            if r.get('jishi'):
                lines.append(f"- 吉時：{', '.join(r['jishi'])}")
            
            if r.get('ji_shen'):
                lines.append(f"- 吉神：{', '.join(r['ji_shen'])}")
            if r.get('xiong_shen'):
                lines.append(f"- 凶神：{', '.join(r['xiong_shen'])}")
            if r.get('warnings'):
                lines.append(f"- ⚠️ 注意：{', '.join(r['warnings'])}")
            
            lines.append("")
        
        # 備註
        if d.notes:
            lines.append("\n## 📝 備註\n")
            for note in d.notes:
                lines.append(f"- {note}")
        
        lines.append("\n---")
        lines.append("*本報告由北斗命數系統生成*")
        
        return "\n".join(lines)
    
    def to_html(self) -> str:
        """輸出 HTML 格式"""
        if not self.data:
            return ""
        
        d = self.data
        type_names = {"marry": "嫁娶擇日", "ground": "動土擇日", "event": d.params.get("event_type", "擇日")}
        title = type_names.get(d.report_type, "擇日")
        
        html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}報告 - 北斗命數</title>
    {REPORT_CSS}
</head>
<body>
    <div class="header">
        <h1>📅 {title}報告</h1>
        <p>生成時間：{d.generated_at} | 查詢範圍：{d.query_range}</p>
    </div>
"""
        
        # 查詢條件
        html += '<div class="info-box"><h2>📋 查詢條件</h2><div class="info-grid">'
        if d.report_type == "marry":
            html += f'''
                <div class="info-item"><label>男方</label><span>{d.params['man_year']}年（{d.params['man_sx']}）</span></div>
                <div class="info-item"><label>女方</label><span>{d.params['woman_year']}年（{d.params['woman_sx']}）</span></div>
                <div class="info-item"><label>大利月</label><span>{d.params['dali_yue']}</span></div>
                <div class="info-item"><label>小利月</label><span>{d.params['xiaoli_yue']}</span></div>
            '''
        elif d.report_type == "ground":
            html += f'''
                <div class="info-item"><label>屋主</label><span>{d.params['owner_year']}年（{d.params['owner_sx']}）</span></div>
                <div class="info-item"><label>坐向</label><span>{d.params.get('zuoxiang', '未指定')}</span></div>
            '''
        else:
            html += f'''
                <div class="info-item"><label>用途</label><span>{d.params.get('event_type', '擇日')}</span></div>
                <div class="info-item"><label>事主</label><span>{d.params.get('owner_sx', '未指定')}</span></div>
            '''
        html += '</div></div>'
        
        # 結果
        for i, r in enumerate(d.results, 1):
            mark = ""
            if d.report_type == "marry":
                if r.get("is_dali"): mark = '<span class="tag good">★大利</span>'
                elif r.get("is_xiaoli"): mark = '<span class="tag neutral">○小利</span>'
            
            html += f'''
    <div class="result-card">
        <div class="result-header">
            <span class="result-date">#{i} {r['date']}（週{r['weekday']}）{r['ganzhi']} {mark}</span>
            <span class="result-score">{r['score']:.0f} 分</span>
        </div>
        <div class="rike-box">
            <div class="label">完整日課</div>
            <div class="value">{r['full_rike']}</div>
        </div>
        <div class="detail-grid">
            <div class="detail-item"><div class="label">農曆</div><div class="value">{r['lunar']}</div></div>
            <div class="detail-item"><div class="label">黃道</div><div class="value">{r['huangdao']}</div></div>
            <div class="detail-item"><div class="label">建除</div><div class="value">{r['jianchu']}</div></div>
            <div class="detail-item"><div class="label">二十八宿</div><div class="value">{r['xiu']}</div></div>
            <div class="detail-item"><div class="label">沖煞</div><div class="value">{r['chong_sha']}</div></div>
            <div class="detail-item"><div class="label">最佳時辰</div><div class="value">{r['best_hour']}</div></div>
        </div>
'''
            
            if r.get('jishi'):
                html += '<div class="jishi-list">'
                for j in r['jishi']:
                    html += f'<span class="jishi-item">{j}</span>'
                html += '</div>'
            
            html += '<div class="tag-list">'
            for j in r.get('ji_shen', []):
                html += f'<span class="tag good">{j}</span>'
            for x in r.get('xiong_shen', []):
                html += f'<span class="tag bad">{x}</span>'
            for w in r.get('warnings', []):
                html += f'<span class="tag bad">⚠️{w}</span>'
            html += '</div></div>'
        
        # 備註
        if d.notes:
            html += '<div class="info-box"><h2>📝 備註</h2><ul>'
            for note in d.notes:
                html += f'<li>{note}</li>'
            html += '</ul></div>'
        
        html += '''
    <div class="footer">
        本報告由北斗命數系統生成<br>
        © 2026 BeiDou MingShu
    </div>
</body>
</html>'''
        
        return html
    
    def save(self, filepath: str, format: str = "html"):
        """儲存報告"""
        if format == "html":
            content = self.to_html()
        elif format == "md":
            content = self.to_markdown()
        else:
            raise ValueError(f"不支援的格式：{format}")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return filepath


# ════════════════════════════════════════════════════════════════════
# L3: 便捷函數
# ════════════════════════════════════════════════════════════════════

def generate_marry_report(man_year: int, woman_year: int, 
                          start: date, end: date, 
                          output_path: str = None, format: str = "html"):
    """生成嫁娶擇日報告"""
    gen = DateReportGenerator()
    gen.generate_marry_report(man_year, woman_year, start, end)
    
    if output_path:
        gen.save(output_path, format)
    
    return gen

def generate_ground_report(owner_year: int, start: date, end: date,
                           zuoxiang: str = None,
                           output_path: str = None, format: str = "html"):
    """生成動土擇日報告"""
    gen = DateReportGenerator()
    gen.generate_ground_report(owner_year, start, end, zuoxiang)
    
    if output_path:
        gen.save(output_path, format)
    
    return gen

def generate_event_report(event_type: str, start: date, end: date,
                          owner_year: int = None,
                          output_path: str = None, format: str = "html"):
    """生成多用途擇日報告"""
    gen = DateReportGenerator()
    gen.generate_event_report(event_type, start, end, owner_year)
    
    if output_path:
        gen.save(output_path, format)
    
    return gen


# ════════════════════════════════════════════════════════════════════
# 測試
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 60)
    print("        擇日報告生成器 - 測試")
    print("═" * 60)
    
    # 測試嫁娶報告
    print("\n【嫁娶報告】")
    gen = generate_marry_report(
        man_year=1990, woman_year=1992,
        start=date(2026, 3, 1), end=date(2026, 3, 31),
        output_path="/tmp/marry_report.html"
    )
    print(f"  已生成：/tmp/marry_report.html")
    print(f"  結果數：{len(gen.data.results)}")
    
    # 測試動土報告
    print("\n【動土報告】")
    gen = generate_ground_report(
        owner_year=1985,
        start=date(2026, 3, 1), end=date(2026, 3, 31),
        zuoxiang="坐北朝南",
        output_path="/tmp/ground_report.html"
    )
    print(f"  已生成：/tmp/ground_report.html")
    print(f"  結果數：{len(gen.data.results)}")
    
    # Markdown 輸出
    print("\n【Markdown 預覽】")
    md = gen.to_markdown()
    print(md[:500] + "...")
    
    print("\n" + "═" * 60)
    print("✅ 報告生成測試完成")
    print("═" * 60)
