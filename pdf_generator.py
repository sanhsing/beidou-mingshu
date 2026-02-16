"""
PDF 報告生成器 pdf_generator.py v1.0
===================================
XTF任務：消-E3 | 執行星：星殼（架構）

核心本質：PDF = 報告文字 + 格式模板

📚 使用 reportlab 生成專業 PDF 報告
支援中文字體（需要安裝字體）
"""

from typing import Dict, Optional
from datetime import datetime
import os

# 嘗試導入 reportlab
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def check_reportlab() -> bool:
    """檢查 reportlab 是否可用"""
    return REPORTLAB_AVAILABLE


def register_chinese_font() -> bool:
    """註冊中文字體"""
    if not REPORTLAB_AVAILABLE:
        return False
    
    # 嘗試常見的中文字體路徑
    font_paths = [
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        # Linux
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        # Windows
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', path))
                return True
            except:
                continue
    
    return False


def generate_pdf_report(
    report_text: str,
    output_path: str,
    title: str = "北斗命數分析報告",
) -> bool:
    """
    生成 PDF 報告
    
    Args:
        report_text: 報告文字內容
        output_path: 輸出路徑
        title: 報告標題
        
    Returns:
        是否成功
    """
    if not REPORTLAB_AVAILABLE:
        print("❌ reportlab 未安裝，無法生成 PDF")
        print("   請執行: pip install reportlab")
        return False
    
    try:
        # 嘗試註冊中文字體
        has_chinese_font = register_chinese_font()
        
        # 建立文檔
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )
        
        # 設定樣式
        styles = getSampleStyleSheet()
        
        # 標題樣式
        if has_chinese_font:
            title_style = ParagraphStyle(
                'ChineseTitle',
                parent=styles['Heading1'],
                fontName='ChineseFont',
                fontSize=18,
                spaceAfter=30,
                alignment=1,  # 居中
            )
            normal_style = ParagraphStyle(
                'ChineseNormal',
                parent=styles['Normal'],
                fontName='ChineseFont',
                fontSize=10,
                leading=14,
            )
        else:
            title_style = styles['Heading1']
            normal_style = styles['Normal']
        
        # 建立內容
        story = []
        
        # 標題
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))
        
        # 生成時間
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"生成時間：{time_str}", normal_style))
        story.append(Spacer(1, 20))
        
        # 報告內容（按行處理）
        lines = report_text.split('\n')
        for line in lines:
            if not line.strip():
                story.append(Spacer(1, 6))
            elif line.startswith('╔') or line.startswith('╚') or line.startswith('┏') or line.startswith('┗'):
                # 跳過框線
                continue
            elif line.startswith('║') or line.startswith('┃'):
                # 處理框線內文字
                text = line.strip('║┃ ')
                if text:
                    story.append(Paragraph(text, normal_style))
            elif line.startswith('【') or line.startswith('★'):
                # 標題行
                story.append(Spacer(1, 10))
                story.append(Paragraph(f"<b>{line}</b>", normal_style))
            else:
                story.append(Paragraph(line, normal_style))
        
        # 頁尾
        story.append(Spacer(1, 30))
        story.append(Paragraph("—— 北斗命數 × 場論詮釋 ——", normal_style))
        
        # 生成 PDF
        doc.build(story)
        print(f"✅ PDF 報告已生成：{output_path}")
        return True
        
    except Exception as e:
        print(f"❌ PDF 生成失敗：{e}")
        return False


def text_to_simple_pdf(
    report_text: str,
    output_path: str,
) -> bool:
    """
    簡化版：純文字轉 PDF（使用等寬字體）
    
    這是一個簡化版本，不需要中文字體
    適合已經格式化好的文字報告
    """
    if not REPORTLAB_AVAILABLE:
        return False
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # 設定起始位置
        x = 2 * cm
        y = height - 2 * cm
        line_height = 12
        
        # 逐行寫入
        lines = report_text.split('\n')
        for line in lines:
            if y < 2 * cm:
                # 換頁
                c.showPage()
                y = height - 2 * cm
            
            # 嘗試使用 Courier 字體（等寬）
            c.setFont("Courier", 8)
            c.drawString(x, y, line[:100])  # 限制每行長度
            y -= line_height
        
        c.save()
        return True
        
    except Exception as e:
        print(f"❌ 簡化 PDF 生成失敗：{e}")
        return False


class PDFReportBuilder:
    """PDF 報告建構器（進階版）"""
    
    def __init__(self, title: str = "北斗命數分析報告"):
        self.title = title
        self.sections = []
        self.has_chinese_font = False
        
        if REPORTLAB_AVAILABLE:
            self.has_chinese_font = register_chinese_font()
    
    def add_section(self, title: str, content: str):
        """添加區塊"""
        self.sections.append({"title": title, "content": content})
    
    def add_table(self, headers: list, rows: list):
        """添加表格"""
        self.sections.append({
            "type": "table",
            "headers": headers,
            "rows": rows,
        })
    
    def build(self, output_path: str) -> bool:
        """建構 PDF"""
        if not REPORTLAB_AVAILABLE:
            return False
        
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # 標題
            story.append(Paragraph(self.title, styles['Heading1']))
            story.append(Spacer(1, 20))
            
            # 區塊
            for section in self.sections:
                if section.get("type") == "table":
                    # 表格
                    data = [section["headers"]] + section["rows"]
                    t = Table(data)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 20))
                else:
                    # 文字區塊
                    story.append(Paragraph(f"<b>{section['title']}</b>", styles['Heading2']))
                    story.append(Spacer(1, 10))
                    for line in section['content'].split('\n'):
                        if line.strip():
                            story.append(Paragraph(line, styles['Normal']))
                    story.append(Spacer(1, 20))
            
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"❌ PDF 建構失敗：{e}")
            return False


# ============================================================
# 便捷函數
# ============================================================

def save_report_as_pdf(
    report_text: str,
    name: str = "report",
    output_dir: str = ".",
) -> Optional[str]:
    """
    儲存報告為 PDF
    
    Returns:
        成功返回檔案路徑，失敗返回 None
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"beidou_{name}_{timestamp}.pdf"
    output_path = os.path.join(output_dir, filename)
    
    if generate_pdf_report(report_text, output_path):
        return output_path
    return None


if __name__ == "__main__":
    print("PDF 生成器測試")
    print(f"reportlab 可用：{REPORTLAB_AVAILABLE}")
    
    if REPORTLAB_AVAILABLE:
        # 測試生成
        test_report = """
北斗命數分析報告

【基本資料】
姓名：測試用戶
性別：男

【八字分析】
日主：庚金
特質：剛毅果斷，重義氣

【場論詮釋】
你的核心能量是「收斂聚合場」
適合方向：金融、法律、技術
"""
        
        success = generate_pdf_report(
            test_report,
            "test_report.pdf",
            "測試報告",
        )
        
        if success:
            print("測試成功！")
        else:
            print("測試失敗")
    else:
        print("請安裝 reportlab: pip install reportlab")
