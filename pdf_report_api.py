#!/usr/bin/env python3
"""
pdf_report_api.py - PDF 報告生成及下載 API
版本：v1.0.0

═══════════════════════════════════════════════════════════════════════
功能：
  • 擇日報告 PDF
  • 紫微命盤 PDF
  • 八字分析 PDF
  • 合婚報告 PDF
  • 綜合報告 PDF
  • FastAPI 下載端點
═══════════════════════════════════════════════════════════════════════

XTF Task Chain
@11星協作：@織明(統籌) @璃語(樣式) @流祇(API)
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import date, datetime
from io import BytesIO
import os

# FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel

# ReportLab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# 導入命理模組
from date_base import get_ganzhi_from_date, get_full_rike, get_lunar_info, DIZHI, SHENGXIAO
from marry_date import MarryDateSelector
from ground_date import GroundDateSelector
from event_date import EventDateSelector, EventType
from ziwei_engine_v1 import create_ziwei_chart, GONG_12
from meihua_engine import full_meihua, GUA_NAME
from bazi_base import analyze_bazi, calc_dayun, calc_liunian_simple, HAS_DAYUN
from chart_matching import match_charts

# ════════════════════════════════════════════════════════════════════
# L0: 字體設置
# ════════════════════════════════════════════════════════════════════

def register_fonts():
    """註冊中文字體"""
    font_paths = [
        # Linux
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        # Windows
        "C:/Windows/Fonts/msyh.ttc",
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', path))
                return True
            except:
                continue
    
    # 使用備用字體
    return False

# 初始化字體
HAS_CHINESE_FONT = register_fonts()
FONT_NAME = 'ChineseFont' if HAS_CHINESE_FONT else 'Helvetica'

# ════════════════════════════════════════════════════════════════════
# L1: 樣式定義
# ════════════════════════════════════════════════════════════════════

def get_styles():
    """獲取報告樣式"""
    styles = getSampleStyleSheet()
    
    # 標題樣式
    styles.add(ParagraphStyle(
        name='ReportTitle',
        fontName=FONT_NAME,
        fontSize=24,
        leading=30,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#302b63')
    ))
    
    # 副標題
    styles.add(ParagraphStyle(
        name='ReportSubtitle',
        fontName=FONT_NAME,
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=30,
        textColor=colors.HexColor('#666666')
    ))
    
    # 章節標題
    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontName=FONT_NAME,
        fontSize=16,
        leading=22,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.HexColor('#1a1a2e'),
        borderPadding=5,
    ))
    
    # 正文
    styles.add(ParagraphStyle(
        name='ReportBody',
        fontName=FONT_NAME,
        fontSize=11,
        leading=18,
        spaceAfter=8,
        textColor=colors.HexColor('#333333')
    ))
    
    # 重點
    styles.add(ParagraphStyle(
        name='Highlight',
        fontName=FONT_NAME,
        fontSize=14,
        leading=20,
        alignment=TA_CENTER,
        spaceBefore=10,
        spaceAfter=10,
        textColor=colors.HexColor('#ffd700'),
        backColor=colors.HexColor('#302b63'),
    ))
    
    # 小字
    styles.add(ParagraphStyle(
        name='Small',
        fontName=FONT_NAME,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#888888')
    ))
    
    return styles


# ════════════════════════════════════════════════════════════════════
# L2: PDF 生成器基礎類
# ════════════════════════════════════════════════════════════════════

class PDFReportGenerator:
    """PDF 報告生成器基礎類"""
    
    def __init__(self):
        self.styles = get_styles()
        self.story = []
        self.buffer = BytesIO()
    
    def add_title(self, title: str, subtitle: str = None):
        """添加標題"""
        self.story.append(Paragraph(title, self.styles['ReportTitle']))
        if subtitle:
            self.story.append(Paragraph(subtitle, self.styles['ReportSubtitle']))
        self.story.append(HRFlowable(
            width="100%", thickness=2, 
            color=colors.HexColor('#ffd700'),
            spaceBefore=10, spaceAfter=20
        ))
    
    def add_section(self, title: str):
        """添加章節標題"""
        self.story.append(Spacer(1, 10))
        self.story.append(Paragraph(f"▌ {title}", self.styles['SectionTitle']))
    
    def add_text(self, text: str):
        """添加正文"""
        self.story.append(Paragraph(text, self.styles['ReportBody']))
    
    def add_highlight(self, text: str):
        """添加重點"""
        self.story.append(Paragraph(f"  {text}  ", self.styles['Highlight']))
    
    def add_table(self, data: List[List[str]], col_widths: List[float] = None):
        """添加表格"""
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#302b63')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        self.story.append(table)
        self.story.append(Spacer(1, 15))
    
    def add_spacer(self, height: float = 20):
        """添加間隔"""
        self.story.append(Spacer(1, height))
    
    def add_page_break(self):
        """添加分頁"""
        self.story.append(PageBreak())
    
    def add_footer(self):
        """添加頁腳"""
        self.story.append(Spacer(1, 30))
        self.story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
        self.story.append(Spacer(1, 10))
        
        # 反詐提示
        anti_fraud = "⚠️ 本報告為娛樂參考性質。若有人以此要求您支付額外費用，請撥打 165 反詐騙專線。"
        self.story.append(Paragraph(anti_fraud, self.styles['Small']))
        self.story.append(Spacer(1, 5))
        
        footer_text = f"北斗命數系統 | 生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self.story.append(Paragraph(footer_text, self.styles['Small']))
    
    def build(self, filename: str = None) -> bytes:
        """構建 PDF"""
        if filename:
            doc = SimpleDocTemplate(filename, pagesize=A4,
                                    leftMargin=2*cm, rightMargin=2*cm,
                                    topMargin=2*cm, bottomMargin=2*cm)
            doc.build(self.story)
            with open(filename, 'rb') as f:
                return f.read()
        else:
            doc = SimpleDocTemplate(self.buffer, pagesize=A4,
                                    leftMargin=2*cm, rightMargin=2*cm,
                                    topMargin=2*cm, bottomMargin=2*cm)
            doc.build(self.story)
            self.buffer.seek(0)
            return self.buffer.getvalue()


# ════════════════════════════════════════════════════════════════════
# L3: 各類型報告生成
# ════════════════════════════════════════════════════════════════════

class DatePDFReport(PDFReportGenerator):
    """擇日 PDF 報告"""
    
    def generate_marry(self, man_year: int, woman_year: int,
                       start: date, end: date, top_n: int = 5) -> bytes:
        """生成嫁娶報告"""
        man_zhi = DIZHI[(man_year - 4) % 12]
        woman_zhi = DIZHI[(woman_year - 4) % 12]
        man_sx = SHENGXIAO[DIZHI.index(man_zhi)]
        woman_sx = SHENGXIAO[DIZHI.index(woman_zhi)]
        
        selector = MarryDateSelector(man_zhi, woman_zhi)
        candidates = selector.select_dates(start, end, top_n)
        
        # 標題
        self.add_title("嫁娶擇日報告", f"查詢範圍：{start} ~ {end}")
        
        # 基本資訊
        self.add_section("查詢條件")
        info_data = [
            ["項目", "內容"],
            ["男方", f"{man_year}年（{man_sx}）"],
            ["女方", f"{woman_year}年（{woman_sx}）"],
            ["大利月", str(selector.dali_yue)],
            ["小利月", str(selector.xiaoli_yue)],
        ]
        self.add_table(info_data, [4*cm, 10*cm])
        
        # 推薦日期
        self.add_section("推薦吉日")
        
        for i, c in enumerate(candidates, 1):
            rike = c.full_rike
            
            # 日期標題
            mark = ""
            if c.is_dali_yue: mark = " [大利]"
            elif c.is_xiaoli_yue: mark = " [小利]"
            
            self.add_text(f"<b>#{i} {c.date}（{c.ganzhi}）{mark}</b>")
            
            # 完整日課
            if rike:
                self.add_highlight(rike.full_rike)
            
            # 詳細資訊
            detail_data = [
                ["黃道", "建除", "二十八宿", "沖煞", "評分"],
                [c.huangdao_shen, c.jianchu, c.xiu, 
                 f"沖{c.chong_sx}煞{c.sha_fang}", f"{c.score.weighted_total:.0f}分"],
            ]
            self.add_table(detail_data)
            
            # 吉時
            if rike and rike.jishi_list:
                jishi = ", ".join([gz for _, gz, _ in rike.jishi_list[:4]])
                self.add_text(f"吉時選項：{jishi}")
            
            self.add_spacer(10)
        
        self.add_footer()
        return self.build()
    
    def generate_ground(self, owner_year: int, start: date, end: date,
                        zuoxiang: str = None, top_n: int = 5) -> bytes:
        """生成動土報告"""
        owner_zhi = DIZHI[(owner_year - 4) % 12]
        owner_sx = SHENGXIAO[DIZHI.index(owner_zhi)]
        
        selector = GroundDateSelector(owner_zhi, zuoxiang=zuoxiang)
        candidates = selector.select_dates(start, end, top_n)
        
        self.add_title("動土擇日報告", f"查詢範圍：{start} ~ {end}")
        
        self.add_section("查詢條件")
        info_data = [
            ["項目", "內容"],
            ["屋主", f"{owner_year}年（{owner_sx}）"],
            ["坐向", zuoxiang or "未指定"],
        ]
        self.add_table(info_data, [4*cm, 10*cm])
        
        self.add_section("推薦吉日")
        
        for i, c in enumerate(candidates, 1):
            rike = c.full_rike
            self.add_text(f"<b>#{i} {c.date}（{c.ganzhi}）</b>")
            
            if rike:
                self.add_highlight(rike.full_rike)
            
            detail_data = [
                ["黃道", "建除", "沖煞", "評分"],
                [c.huangdao_shen, c.jianchu, 
                 f"沖{c.chong_sx}煞{c.sha_fang}", f"{c.score.weighted_total:.0f}分"],
            ]
            self.add_table(detail_data)
            self.add_spacer(10)
        
        self.add_footer()
        return self.build()


class ZiweiPDFReport(PDFReportGenerator):
    """紫微斗數 PDF 報告"""
    
    def generate(self, year_gan: str, year_zhi: str,
                 lunar_month: int, lunar_day: int,
                 hour_zhi: str, gender: str) -> bytes:
        """生成紫微報告"""
        chart = create_ziwei_chart(year_gan, year_zhi, lunar_month, lunar_day, hour_zhi, gender)
        
        self.add_title("紫微斗數命盤", 
                       f"{year_gan}{year_zhi}年 {lunar_month}月{lunar_day}日 {hour_zhi}時 {gender}")
        
        # 基本資訊
        self.add_section("命盤概要")
        info_data = [
            ["項目", "內容"],
            ["命宮", GONG_12[chart.ming_gong_idx]],
            ["身宮", GONG_12[chart.shen_gong_idx]],
            ["五行局", f"{chart.ju_shu}局"],
        ]
        self.add_table(info_data, [4*cm, 10*cm])
        
        # 十二宮
        self.add_section("十二宮星曜")
        gong_data = [["宮位", "地支", "主星", "輔星", "四化"]]
        
        for i, gong in enumerate(chart.gongs):
            main = ", ".join(gong.main_stars) if gong.main_stars else "-"
            aux = ", ".join(gong.lucky_stars + gong.evil_stars) if (gong.lucky_stars or gong.evil_stars) else "-"
            sihua = ", ".join(gong.sihua) if gong.sihua else "-"
            gong_data.append([gong.name, gong.zhi, main, aux, sihua])
        
        self.add_table(gong_data, [2.5*cm, 2*cm, 4*cm, 4*cm, 3*cm])
        
        self.add_footer()
        return self.build()


class BaziPDFReport(PDFReportGenerator):
    """八字分析 PDF 報告"""
    
    def generate(self, year_gz: str, month_gz: str,
                 day_gz: str, hour_gz: str,
                 birth_year: int = None, birth_month: int = None,
                 birth_day: int = None, gender: str = None) -> bytes:
        """生成八字報告"""
        chart = analyze_bazi(year_gz, month_gz, day_gz, hour_gz)
        
        self.add_title("八字命理分析", f"{year_gz} {month_gz} {day_gz} {hour_gz}")
        
        # 四柱
        self.add_section("四柱八字")
        pillar_data = [
            ["", "年柱", "月柱", "日柱", "時柱"],
            ["天干", year_gz[0], month_gz[0], day_gz[0], hour_gz[0]],
            ["地支", year_gz[1], month_gz[1], day_gz[1], hour_gz[1]],
        ]
        self.add_table(pillar_data, [2*cm, 3*cm, 3*cm, 3*cm, 3*cm])
        
        # 命理分析
        self.add_section("命理分析")
        analysis_data = [
            ["項目", "內容"],
            ["日主", f"{chart.day_master}（{chart.day_master_wx}）"],
            ["用神", chart.yongshen],
            ["喜神", str(chart.xishen)],
            ["忌神", str(chart.jishen)],
            ["生肖", chart.shengxiao],
        ]
        self.add_table(analysis_data, [4*cm, 10*cm])
        
        # 大運（如果有出生資料）
        if HAS_DAYUN and birth_year and gender:
            dayun = calc_dayun(year_gz, month_gz, gender, birth_year, birth_month or 1, birth_day or 1)
            if dayun:
                self.add_section("大運")
                self.add_text(f"起運歲數：{dayun.qiyun_age}歲（{dayun.direction}）")
                
                dayun_data = [["運次", "干支", "起始年齡", "結束年齡"]]
                for d in dayun.dayun_list[:6]:
                    dayun_data.append([f"第{d.order}運", d.ganzhi, str(d.start_age), str(d.end_age)])
                self.add_table(dayun_data, [2.5*cm, 3*cm, 4*cm, 4*cm])
        
        self.add_footer()
        return self.build()


class MatchPDFReport(PDFReportGenerator):
    """合婚 PDF 報告"""
    
    def generate(self, person1: Dict, person2: Dict, match_type: str = "marriage") -> bytes:
        """生成合婚報告"""
        result = match_charts(person1, person2, match_type)
        
        type_name = {"marriage": "合婚", "parent": "親子", "partner": "合作"}.get(match_type, "配對")
        
        self.add_title(f"{type_name}分析報告", 
                       f"{person1.get('name', '甲方')} × {person2.get('name', '乙方')}")
        
        # 雙方資料
        self.add_section("雙方資料")
        info_data = [
            ["", person1.get('name', '甲方'), person2.get('name', '乙方')],
            ["性別", person1.get('gender', '-'), person2.get('gender', '-')],
            ["日主", person1.get('day_master', '-'), person2.get('day_master', '-')],
            ["年支", person1.get('year_zhi', '-'), person2.get('year_zhi', '-')],
        ]
        self.add_table(info_data, [3*cm, 5*cm, 5*cm])
        
        # 結果
        self.add_section("分析結果")
        self.add_highlight(f"契合度：{result['percentage']}%（{result['grade']}級）")
        self.add_text(result['summary'])
        
        # 詳細因素
        self.add_section("詳細因素")
        factor_data = [["因素", "評分", "說明"]]
        for f in result['factors']:
            factor_data.append([f['name'], f"{f['score']}分", f['description']])
        self.add_table(factor_data, [4*cm, 2*cm, 8*cm])
        
        # 建議
        if result.get('advice'):
            self.add_section("建議")
            for advice in result['advice']:
                self.add_text(f"• {advice}")
        
        self.add_footer()
        return self.build()


class EventPDFReport(PDFReportGenerator):
    """多用途擇日 PDF 報告"""
    
    def generate(self, event_type: str, start: date, end: date,
                 owner_year: int = None, top_n: int = 5) -> bytes:
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
        
        self.add_title(f"{event_type}擇日報告", f"查詢範圍：{start} ~ {end}")
        
        # 基本資訊
        self.add_section("查詢條件")
        info_data = [
            ["項目", "內容"],
            ["用途", event_type],
            ["事主", f"{owner_year}年（{owner_sx}）" if owner_sx else "未指定"],
        ]
        self.add_table(info_data, [4*cm, 10*cm])
        
        # 推薦日期
        self.add_section("推薦吉日")
        
        for i, c in enumerate(candidates, 1):
            rike = c.full_rike
            self.add_text(f"<b>#{i} {c.date}（{c.ganzhi}）</b>")
            
            if rike:
                self.add_highlight(rike.full_rike)
            
            detail_data = [
                ["黃道", "建除", "二十八宿", "沖煞", "評分"],
                [c.huangdao_shen, c.jianchu, c.xiu, 
                 f"沖{c.chong_sx}煞{c.sha_fang}", f"{c.score.weighted_total:.0f}分"],
            ]
            self.add_table(detail_data)
            
            if rike and rike.jishi_list:
                jishi = ", ".join([gz for _, gz, _ in rike.jishi_list[:4]])
                self.add_text(f"吉時選項：{jishi}")
            
            self.add_spacer(10)
        
        self.add_footer()
        return self.build()


class MeihuaPDFReport(PDFReportGenerator):
    """梅花易數 PDF 報告"""
    
    def generate(self, year_zhi_num: int, lunar_month: int,
                 lunar_day: int, hour_zhi_num: int,
                 question: str = None) -> bytes:
        """生成梅花易數報告"""
        result = full_meihua(year_zhi_num, lunar_month, lunar_day, hour_zhi_num)
        
        ben = result['ben_gua']
        bian = result['bian_gua']
        hu = result['hu_gua']
        ty = result['ti_yong']
        
        self.add_title("梅花易數占卜報告", 
                       f"起卦時間：{lunar_month}月{lunar_day}日")
        
        if question:
            self.add_section("占問事項")
            self.add_text(question)
        
        # 卦象
        self.add_section("卦象")
        gua_data = [
            ["", "上卦", "下卦", "動爻"],
            ["本卦", GUA_NAME[ben.upper], GUA_NAME[ben.lower], f"第{ben.dong_yao}爻"],
            ["變卦", GUA_NAME[bian.upper], GUA_NAME[bian.lower], "-"],
            ["互卦", GUA_NAME[hu.upper], GUA_NAME[hu.lower], "-"],
        ]
        self.add_table(gua_data, [3*cm, 4*cm, 4*cm, 3*cm])
        
        # 體用分析
        self.add_section("體用分析")
        ty_data = [
            ["項目", "內容"],
            ["體卦", f"{ty.ti_name}（{ty.ti_wx}）"],
            ["用卦", f"{ty.yong_name}（{ty.yong_wx}）"],
            ["關係", ty.relation],
        ]
        self.add_table(ty_data, [4*cm, 10*cm])
        
        # 判斷
        self.add_section("斷卦")
        self.add_highlight(ty.verdict)
        
        # 詳細分析
        if hasattr(ty, 'hu_analysis') and ty.hu_analysis:
            self.add_text(f"互卦分析：{ty.hu_analysis}")
        if hasattr(ty, 'bian_analysis') and ty.bian_analysis:
            self.add_text(f"變卦分析：{ty.bian_analysis}")
        
        self.add_footer()
        return self.build()


# ════════════════════════════════════════════════════════════════════
# L4: FastAPI 下載端點
# ════════════════════════════════════════════════════════════════════

app = FastAPI(title="北斗命數 PDF API", version="1.0.0")

class MarryPDFRequest(BaseModel):
    man_year: int
    woman_year: int
    start_date: str
    end_date: str
    top_n: int = 5

class GroundPDFRequest(BaseModel):
    owner_year: int
    start_date: str
    end_date: str
    zuoxiang: Optional[str] = None
    top_n: int = 5

class ZiweiPDFRequest(BaseModel):
    year_gan: str
    year_zhi: str
    lunar_month: int
    lunar_day: int
    hour_zhi: str
    gender: str = "男"

class BaziPDFRequest(BaseModel):
    year_gz: str
    month_gz: str
    day_gz: str
    hour_gz: str
    birth_year: Optional[int] = None
    birth_month: Optional[int] = None
    birth_day: Optional[int] = None
    gender: Optional[str] = None

class MatchPDFRequest(BaseModel):
    person1: Dict[str, str]
    person2: Dict[str, str]
    match_type: str = "marriage"

class EventPDFRequest(BaseModel):
    event_type: str  # 開市/搬家/安床/祭祀/出行
    start_date: str
    end_date: str
    owner_year: Optional[int] = None
    top_n: int = 5

class MeihuaPDFRequest(BaseModel):
    year_zhi_num: int
    lunar_month: int
    lunar_day: int
    hour_zhi_num: int
    question: Optional[str] = None


@app.post("/api/pdf/marry")
async def pdf_marry(req: MarryPDFRequest):
    """下載嫁娶擇日 PDF"""
    try:
        start = date.fromisoformat(req.start_date)
        end = date.fromisoformat(req.end_date)
    except:
        raise HTTPException(400, "日期格式錯誤")
    
    gen = DatePDFReport()
    pdf_bytes = gen.generate_marry(req.man_year, req.woman_year, start, end, req.top_n)
    
    filename = f"marry_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.post("/api/pdf/ground")
async def pdf_ground(req: GroundPDFRequest):
    """下載動土擇日 PDF"""
    try:
        start = date.fromisoformat(req.start_date)
        end = date.fromisoformat(req.end_date)
    except:
        raise HTTPException(400, "日期格式錯誤")
    
    gen = DatePDFReport()
    pdf_bytes = gen.generate_ground(req.owner_year, start, end, req.zuoxiang, req.top_n)
    
    filename = f"ground_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.post("/api/pdf/ziwei")
async def pdf_ziwei(req: ZiweiPDFRequest):
    """下載紫微命盤 PDF"""
    gen = ZiweiPDFReport()
    pdf_bytes = gen.generate(
        req.year_gan, req.year_zhi,
        req.lunar_month, req.lunar_day,
        req.hour_zhi, req.gender
    )
    
    filename = f"ziwei_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.post("/api/pdf/bazi")
async def pdf_bazi(req: BaziPDFRequest):
    """下載八字分析 PDF"""
    gen = BaziPDFReport()
    pdf_bytes = gen.generate(
        req.year_gz, req.month_gz, req.day_gz, req.hour_gz,
        req.birth_year, req.birth_month, req.birth_day, req.gender
    )
    
    filename = f"bazi_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.post("/api/pdf/match")
async def pdf_match(req: MatchPDFRequest):
    """下載合婚分析 PDF"""
    gen = MatchPDFReport()
    pdf_bytes = gen.generate(req.person1, req.person2, req.match_type)
    
    filename = f"match_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.post("/api/pdf/event")
async def pdf_event(req: EventPDFRequest):
    """下載多用途擇日 PDF（開市/搬家/安床/祭祀/出行）"""
    try:
        start = date.fromisoformat(req.start_date)
        end = date.fromisoformat(req.end_date)
    except:
        raise HTTPException(400, "日期格式錯誤")
    
    gen = EventPDFReport()
    pdf_bytes = gen.generate(req.event_type, start, end, req.owner_year, req.top_n)
    
    filename = f"{req.event_type}_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.post("/api/pdf/meihua")
async def pdf_meihua(req: MeihuaPDFRequest):
    """下載梅花易數 PDF"""
    gen = MeihuaPDFReport()
    pdf_bytes = gen.generate(
        req.year_zhi_num, req.lunar_month,
        req.lunar_day, req.hour_zhi_num,
        req.question
    )
    
    filename = f"meihua_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/api/pdf/status")
async def pdf_status():
    """PDF 模組狀態"""
    return {
        "chinese_font": HAS_CHINESE_FONT,
        "font_name": FONT_NAME,
        "reportlab": True,
    }


# ════════════════════════════════════════════════════════════════════
# 測試
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 60)
    print("        PDF 報告生成器 - 測試")
    print("═" * 60)
    
    print(f"\n字體狀態：{'✅ 中文字體' if HAS_CHINESE_FONT else '⚠️ 英文字體'}")
    
    # 測試嫁娶報告
    print("\n【嫁娶 PDF】")
    gen = DatePDFReport()
    pdf = gen.generate_marry(1990, 1992, date(2026, 3, 1), date(2026, 3, 31))
    with open("/tmp/marry_test.pdf", "wb") as f:
        f.write(pdf)
    print(f"  ✅ 已生成：/tmp/marry_test.pdf ({len(pdf)} bytes)")
    
    # 測試紫微報告
    print("\n【紫微 PDF】")
    gen = ZiweiPDFReport()
    pdf = gen.generate("乙", "丑", 11, 19, "酉", "男")
    with open("/tmp/ziwei_test.pdf", "wb") as f:
        f.write(pdf)
    print(f"  ✅ 已生成：/tmp/ziwei_test.pdf ({len(pdf)} bytes)")
    
    # 測試八字報告
    print("\n【八字 PDF】")
    gen = BaziPDFReport()
    pdf = gen.generate("乙丑", "丁亥", "庚子", "乙酉", 1985, 12, 30, "男")
    with open("/tmp/bazi_test.pdf", "wb") as f:
        f.write(pdf)
    print(f"  ✅ 已生成：/tmp/bazi_test.pdf ({len(pdf)} bytes)")
    
    # 測試合婚報告
    print("\n【合婚 PDF】")
    gen = MatchPDFReport()
    pdf = gen.generate(
        {"name": "男方", "gender": "男", "day_master": "甲", "year_zhi": "午", "month_zhi": "寅", "day_zhi": "子", "hour_zhi": "酉"},
        {"name": "女方", "gender": "女", "day_master": "丙", "year_zhi": "申", "month_zhi": "寅", "day_zhi": "午", "hour_zhi": "卯"},
    )
    with open("/tmp/match_test.pdf", "wb") as f:
        f.write(pdf)
    print(f"  ✅ 已生成：/tmp/match_test.pdf ({len(pdf)} bytes)")
    
    print("\n" + "═" * 60)
    print("✅ PDF 生成測試完成")
    print("═" * 60)
    print("\n啟動 API：uvicorn pdf_report_api:app --port 8001")
