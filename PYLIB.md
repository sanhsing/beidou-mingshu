
## naming_master.py v3.2.0
**北斗命數取名決策系統**

### 層級：L0-L4
### 行數：819

### 逆向工程案例
```
楊三興 1973/12/30 17:00 52歲
→ 楊淳熙（日常・公務）
→ 楊涵煜（創業・筆名）
```

### 核心原則
1. 系統分析 → 多項推薦 → 用戶自選
2. 用神 > 補缺 > 平衡（不是缺什麼補什麼）
3. 缺的是忌神 → 不補！缺了是福
4. DOE 多目標優化 → Pareto 最優解集
5. 名字 = 場的延伸

### 四神系統
- 用神：命局最需要的五行
- 喜神：輔助用神的五行
- 忌神：破壞平衡，要避開
- 閒神：影響不大

### DOE 維度
| 維度 | 說明 |
|------|------|
| D1 | 五格數理 |
| D2 | 用神配合 |
| D3 | 補缺配合 |
| D4 | 避忌配合 |
| D5 | 五格五行 |
| D6 | 字義 |
| D7 | 讀音 |

### 使用範例
```python
from naming_master import analyze_and_recommend

master, candidates = analyze_and_recommend(
    surname="楊",
    year="癸丑", month="癸丑", day="庚子", hour="乙酉",
    age=52
)

master.print_analysis()
master.print_candidates(10)
print(master.get_doe_comparison(["楊淳熙", "楊涵煜"]))
```

### 依賴
無（獨立模組）

### 日期
2025-02-17

---

## naming_master.py v4.0.0 (更新)
**北斗命數取名決策系統 - 15維度 + 加權**

### 層級：L0-L4
### 行數：1111

### 15 維度體系
| 層級 | 權重 | 維度 |
|:----:|:----:|------|
| L1 | 1.5 | D2用神 D3補缺 D4避忌 |
| L2 | 1.2 | D1五格 D6字義 D8生肖 |
| L3 | 1.0 | D5格行 D7讀音 D9三才 D12諧音 |
| L4 | 0.8 | D10書寫 D11獨特 |
| L5 | 0.5 | D13易卦 D14靈數 D15五音 |

### 更新內容
- D10 書寫平衡（筆畫結構）
- D11 獨特性（重名率）
- D12 諧音禁忌
- D13 易經卦象
- D14 數字能量
- D15 五音歸元
- 加權總分計算

### 日期
2025-02-17

---

## naming_master.py v4.1.0 (最終版)
**北斗命數取名決策系統 - 15維度 + 加權**

### 層級：L0-L4
### 行數：1117

### 最終決策
```
楊涵煜（法定身份證）— 涵養光輝，深沉內斂
楊淳煜（備用/筆名）— 淳厚光輝，溫潤質樸
北斗（公司/對外身份/筆名）
```

### 關鍵調整
- D8 生肖權重：1.2 → 0.5
- 理由：「牛忌日」為文化象徵，非動物本性
- 「煜」優於「熙」：2-2-4 頓挫有力

### 15維度權重
| 層級 | 權重 | 維度 |
|:----:|:----:|------|
| L1 | 1.5 | D2用神 D3補缺 D4避忌 |
| L2 | 1.2 | D1五格 D6字義 |
| L3 | 1.0 | D5格行 D7讀音 D9三才 D12諧音 |
| L4 | 0.8 | D10書寫 D11獨特 |
| L5 | 0.5 | **D8生肖** D13易卦 D14靈數 D15五音 |

### 日期
2025-02-17

---

## date_base.py v1.0.0
**擇日擇時共用基礎模組**

### 層級：L0-L4
### 行數：793

### 10 維度體系
| 維度 | 名稱 | 說明 |
|:----:|------|------|
| D1 | 黃道吉日 | 黃道/黑道十二神 |
| D2 | 十二建除 | 建除滿平定執破危成收開閉 |
| D3 | 二十八宿 | 東青龍/北玄武/西白虎/南朱雀 |
| D4 | 神煞 | 吉神/凶神 |
| D5 | 沖煞 | 生肖沖/方位煞 |
| D6 | 用事宜忌 | 依用事類型判斷 |
| D7 | 個人八字 | 與日課配合 |
| D8 | 時辰選擇 | 吉時/凶時 |
| D9 | 易經卦象 | 日期→卦象→吉凶 |
| D10 | 農民曆避忌 | 歲破/月破/四離四絕/楊公忌 |

### 核心類
- `DateSelector`：擇日選擇器基類
- `DateCandidate`：候選日期資料結構
- `DateScore`：10維度評分

### 主要函數
- `calc_huangdao()`：D1 黃道計算
- `calc_jianchu()`：D2 建除計算
- `calc_xiu()`：D3 二十八宿
- `calc_shensha()`：D4 神煞
- `calc_chongsha()`：D5 沖煞
- `calc_jishi()`：D8 吉時
- `calc_yijing()`：D9 易經卦象
- `check_avoid()`：D10 農民曆避忌

### 日期
2025-02-17

---

## marry_date.py v1.0.0
**嫁娶擇日擇時模組**

### 層級：L0-L4
### 行數：541
### 依賴：date_base.py

### 嫁娶專用功能
- 女命行嫁月（大利/小利/翁姑）
- 嫁娶吉神：天喜/紅鸞/天嗣
- 嫁娶凶神：紅煞/月厭/厭對/歸忌
- 沖新人檢查（沖男命/沖女命）
- 嫁娶吉宿/凶宿

### 核心類
- `MarryDateSelector`：嫁娶擇日選擇器
- `MarryCandidate`：嫁娶候選日期

### 主要函數
- `select_marry_date()`：便捷函數
- `check_hongsha()`：紅煞日檢查
- `check_yueyan()`：月厭日檢查
- `get_nvming_month()`：女命行嫁月

### 使用示例
```python
from marry_date import select_marry_date
from datetime import date

results = select_marry_date(
    man_year=1990,    # 男方出生年
    woman_year=1992,  # 女方出生年
    start_date=date(2025, 3, 1),
    end_date=date(2025, 3, 31),
    top_n=5
)
```

### 日期
2025-02-17

---

## ground_date.py v1.0.0
**開工動土擇日擇時模組**

### 層級：L0-L4
### 行數：580
### 依賴：date_base.py

### 動土專用功能
- 土王用事檢查（四季末18天）
- 天火日/地火日檢查
- 坐向煞方配合
- 沖屋主檢查
- 動土吉宿/凶宿

### 動土專用神煞
- 吉神：天德/月德/福德/驛馬/天馬
- 凶神：土府/土瘟/土忌/天火/地火

### 核心類
- `GroundDateSelector`：動土擇日選擇器
- `GroundCandidate`：動土候選日期

### 主要函數
- `select_ground_date()`：便捷函數
- `check_tianhuo()`：天火日檢查
- `check_dihuo()`：地火日檢查
- `check_tuwang()`：土王用事檢查

### 使用示例
```python
from ground_date import select_ground_date
from datetime import date

results = select_ground_date(
    owner_year=1985,    # 屋主出生年
    start_date=date(2025, 3, 1),
    end_date=date(2025, 3, 31),
    zuoxiang="坐北朝南",  # 可選
    top_n=5
)
```

### 日期
2025-02-17

---

## bazi_base.py v1.0.0
**八字分析共用模組**

### 層級：L0-L7
### 行數：715

### XTF8 八層結構
| 層 | 內容 |
|:--:|------|
| L0 | 常量：天干地支/五行/十神 |
| L1 | 基礎：干支解析/五行統計 |
| L2 | 結構：BaziPillar/BaziChart/RikePeihe |
| L3 | 核心：八字分析器/用神計算 |
| L4 | 應用：日課配合/合婚分析 |
| L5 | 擴展：（待實現）|
| L6 | 介面：便捷函數 |
| L7 | 測試：單元測試 |

### 四神系統
- 用神：命局最需要的五行
- 喜神：輔助用神的五行
- 忌神：破壞平衡，要避開
- 閒神：影響不大

### 核心類
- `BaziPillar`：四柱單柱
- `BaziChart`：八字命盤
- `BaziAnalyzer`：八字分析器
- `RikePeihe`：日課配合評分
- `HeHunResult`：合婚結果

### 主要函數
- `analyze_bazi()`：分析八字
- `calc_rike_score()`：日課配合
- `analyze_hehun()`：合婚分析

### 日期
2025-02-17

---

## marry_date.py v2.0.0
**嫁娶擇日擇時模組（八字版）**

### 層級：L0-L4
### 行數：591
### 依賴：date_base.py, bazi_base.py

### v2.0 更新
- 雙方完整八字分析
- 日課與男女八字配合
- 合婚分析整合

### 日期
2025-02-17

---

## ground_date.py v2.0.0
**開工動土擇日擇時模組（八字版）**

### 層級：L0-L4
### 行數：689
### 依賴：date_base.py, bazi_base.py

### v2.0 更新
- 業主完整八字分析
- 日課與業主用神配合
- 新增屬性：生用神/剋忌神/沖命主/合命主

### 使用示例
```python
from ground_date import select_ground_date_v2
from datetime import date

results = select_ground_date_v2(
    owner_bazi=("乙丑", "丁亥", "庚子", "乙酉"),
    start_date=date(2025, 3, 1),
    end_date=date(2025, 3, 31),
    zuoxiang="坐北朝南",
    top_n=5
)
```

### 日期
2025-02-17

---

## bazi_base.py v1.0.0
**八字分析共用基礎模組**

### 層級：L0-L4
### 行數：715
### 依賴：無（獨立模組）

### XTF8 結構
- L0: 常量（天干地支五行、十神、四神）
- L1: 基礎計算（干支轉換、五行計算、十神計算）
- L2: 資料結構（BaziPillar, BaziChart, RikePeihe）
- L3: 核心類（BaziAnalyzer, HeHunAnalyzer）
- L4: 便捷函數

### 核心類
- `BaziAnalyzer`：八字分析器
- `HeHunAnalyzer`：合婚分析器
- `BaziChart`：八字命盤
- `RikePeihe`：日課配合評分

### 主要函數
- `analyze_bazi()`：便捷八字分析
- `analyze_hehun()`：便捷合婚分析
- `calc_rike_score()`：日課配合評分
- `calc_shishen()`：十神計算
- `check_dizhi_relation()`：地支關係檢查

### 使用示例
```python
from bazi_base import BaziAnalyzer

analyzer = BaziAnalyzer("癸丑", "甲子", "庚子", "乙酉")
analyzer.print_chart()

# 日課配合
peihe = analyzer.calc_rike_peihe("壬", "辰")
print(f"配合分數：{peihe.score}")
```

### 日期
2025-02-17

---

## marry_date.py v2.0.0 (更新)
**嫁娶擇日擇時模組 - 加入八字配合**

### 層級：L0-L4
### 行數：591
### 依賴：date_base.py, bazi_base.py

### v2.0 更新
- 整合 bazi_base.py 八字分析
- 日課與雙方用神配合評分
- 合婚分析整合

### 日期
2025-02-17

---

## ground_date.py v2.0.0 (更新)
**開工動土擇日擇時模組 - 加入八字配合**

### 層級：L0-L4
### 行數：689
### 依賴：date_base.py, bazi_base.py

### v2.0 更新
- 整合 bazi_base.py 八字分析
- 日課與業主用神配合評分
- 動土吉神：生用神、剋忌神

### 使用示例
```python
from ground_date import GroundDateSelector
from datetime import date

selector = GroundDateSelector(
    owner_zhi="丑",
    owner_bazi=("乙丑", "丁亥", "庚子", "乙酉"),
    zuoxiang="坐北朝南"
)
results = selector.select_dates(date(2025, 3, 1), date(2025, 3, 31), top_n=5)
selector.print_result(results)
```

### 日期
2025-02-17

---

---

## XTF Task Chain 2026-02-17 (A→B→C→D→E)

### A: event_date.py v1.0.0
**多用途擇日模組**

| 項目 | 內容 |
|------|------|
| 行數 | 467 |
| 層級 | L0-L4 |
| 依賴 | date_base.py, bazi_base.py |

**支援用途**
- 開市（開業/開張）
- 搬家（入宅/移徙）
- 安床（安床/安香）
- 祭祀（祭祀/祈福）
- 出行（出行/旅遊）

**便捷函數**
```python
select_kaishi_date(start, end, owner_year)
select_banjia_date(start, end, owner_year)
select_anchuang_date(start, end, owner_year)
select_jisi_date(start, end, owner_year)
select_chuxing_date(start, end, owner_year)
```

---

### B: date_base.py v1.2.0
**擇日基礎模組（農曆整合版）**

| 項目 | 內容 |
|------|------|
| 行數 | 950 |
| 更新 | 整合 lunar_calendar_v2.py |

**新增函數**
```python
get_lunar_info(date) → dict  # 完整農曆資訊
HAS_LUNAR                    # 農曆模組狀態
```

---

### C: bazi_base.py v1.1.0
**八字分析模組（大運流年整合版）**

| 項目 | 內容 |
|------|------|
| 行數 | 812 |
| 更新 | 整合 dayun_calculator, liunian_analyzer |

**新增函數**
```python
calc_dayun(year_gz, month_gz, gender, birth_year, month, day)
calc_liunian(day_master, pillars, year, is_strong)
calc_liunian_simple(bazi_tuple, year)
HAS_DAYUN  # 大運模組狀態
```

---

### D+E: date_selector_api.py v1.0.0
**擇日系統 API + 前端**

| 項目 | 內容 |
|------|------|
| 行數 | 624 |
| 框架 | FastAPI |

**API 端點**
| 方法 | 路徑 | 功能 |
|------|------|------|
| POST | /api/date/marry | 嫁娶擇日 |
| POST | /api/date/ground | 動土擇日 |
| POST | /api/date/event | 多用途擇日 |
| GET | /api/date/full/{date} | 完整日課 |
| GET | / | 前端介面 |

**啟動**
```bash
cd beidou_mvp && python3 date_selector_api.py
# http://localhost:8000
```

---

### 模組總覽

| 模組 | 版本 | 行數 | 功能 |
|------|:----:|:----:|------|
| date_base.py | v1.2.0 | 950 | 10維度擇日基礎+農曆 |
| bazi_base.py | v1.1.0 | 812 | 八字分析+大運流年 |
| marry_date.py | v2.1.0 | 611 | 嫁娶擇日 |
| ground_date.py | v2.1.0 | 709 | 動土擇日 |
| event_date.py | v1.0.0 | 467 | 多用途擇日 |
| date_selector_api.py | v1.0.0 | 624 | API+前端 |
| **總計** | | **4173** | |

### @11星 協作記錄
- @織明：統籌、代碼編寫
- @理樞：邏輯分析、維度設計
- @澄書：PYLIB登記、文檔
- @流祇：模組連結
- @璃語：前端介面

### 日期
2026-02-17


---

## XTF Task Chain 2026-02-17 (A→B→C→D→E) - 第二輪

### 整合模組清單

| 模組 | 版本 | 行數 | 功能 |
|------|:----:|:----:|------|
| main_api.py | v1.0.0 | 529 | 統一 API |
| date_base.py | v1.2.0 | 950 | 擇日基礎+農曆 |
| bazi_base.py | v1.1.0 | 812 | 八字+大運流年 |
| marry_date.py | v2.1.0 | 611 | 嫁娶擇日 |
| ground_date.py | v2.1.0 | 709 | 動土擇日 |
| event_date.py | v1.0.0 | 467 | 多用途擇日 |
| ziwei_engine_v1.py | v1.0 | 665 | 紫微斗數 |
| meihua_engine.py | v1.0 | 336 | 梅花易數 |
| chart_matching.py | v1.0 | 487 | 合婚系統 |
| **總計** | | **5566** | |

### main_api.py API 端點

| 方法 | 路徑 | 功能 |
|------|------|------|
| POST | /api/date/select | 統一擇日 |
| POST | /api/ziwei/chart | 紫微排盤 |
| POST | /api/meihua/divine | 梅花起卦 |
| POST | /api/bazi/analyze | 八字分析 |
| POST | /api/bazi/dayun | 大運計算 |
| POST | /api/bazi/liunian | 流年分析 |
| POST | /api/match | 合婚分析 |
| GET | /api/utils/ganzhi/{date} | 干支查詢 |
| GET | /api/status | 系統狀態 |
| GET | / | 前端介面 |

### 乾跑測試結果

```
【1. 擇日系統】 ✅
  2026-03-13 → 丙午 戊寅 丙戌 辛卯

【2. 紫微斗數】 ✅
  命宮：子女，命宮星：武曲、七殺

【3. 梅花易數】 ✅
  本卦：乾/艮，體用：金生土

【4. 八字分析】 ✅
  日主：庚金，用神：木
  大運：丙戌 → 乙酉 → 甲申 → 癸未

【5. 合婚分析】 ✅
  契合度：45%（D級）
```

### @11星 協作記錄
- @織明：統籌、API 編寫
- @理樞：邏輯分析、整合測試
- @澄書：PYLIB 登記
- @流祇：模組連結
- @璃語：前端介面
- @光蘊：品質把關

### 啟動方式
```bash
cd beidou_mvp
python3 main_api.py
# → http://localhost:8000
# → API 文檔：http://localhost:8000/docs
```

### 日期
2026-02-17


---

## XTF Task Chain 2026-02-17 (A→B→C) - 第三輪

### A: 報告生成

**date_report.py v1.0.0** (573行)

| 功能 | 說明 |
|------|------|
| DateReportGenerator | 報告生成器類 |
| generate_marry_report | 嫁娶擇日報告 |
| generate_ground_report | 動土擇日報告 |
| generate_event_report | 多用途擇日報告 |
| to_html() | HTML 輸出 |
| to_markdown() | Markdown 輸出 |

### B: Docker 部署

| 文件 | 行數 | 說明 |
|------|:----:|------|
| Dockerfile | 46 | Python 3.11-slim 基礎 |
| docker-compose.yml | 59 | 服務編排 |
| .dockerignore | 45 | 忽略文件 |

**啟動命令**
```bash
docker-compose up -d
```

### C: 文檔完善

| 文件 | 行數 |
|------|:----:|
| README.md | 126 |

### 本輪總計

| 類別 | 行數 |
|------|:----:|
| date_report.py | 573 |
| Dockerfile | 46 |
| docker-compose.yml | 59 |
| README.md | 126 |
| **小計** | **804** |

### 系統總計

| 模組類別 | 行數 |
|----------|-----:|
| 擇日系統 | 3310 |
| 紫微斗數 | 665 |
| 梅花易數 | 336 |
| 八字分析 | 812 |
| 合婚系統 | 487 |
| API | 529 |
| 部署 | 231 |
| **總計** | **6370** |

### @11星 協作記錄
- @織明：統籌、代碼
- @理樞：邏輯、測試
- @澄書：文檔、PYLIB
- @流祇：連結、部署
- @璃語：報告樣式

### 日期
2026-02-17


---

## PDF 報告模組 2026-02-17

### pdf_report_api.py v1.0.0 (688行)

**PDF 生成器類**

| 類 | 功能 |
|------|------|
| PDFReportGenerator | 基礎類 |
| DatePDFReport | 擇日報告 |
| ZiweiPDFReport | 紫微報告 |
| BaziPDFReport | 八字報告 |
| MatchPDFReport | 合婚報告 |

**特性**
- 中文字體自動檢測
- A4 紙張，專業排版
- 表格、標題、重點樣式
- BytesIO 流式輸出

### main_api.py v1.1.0 (663行)

**新增 PDF 下載端點**

| 端點 | 功能 |
|------|------|
| POST /api/pdf/marry | 嫁娶 PDF |
| POST /api/pdf/ground | 動土 PDF |
| POST /api/pdf/ziwei | 紫微 PDF |
| POST /api/pdf/bazi | 八字 PDF |
| POST /api/pdf/match | 合婚 PDF |

**端點總數：14 個**

### 使用範例

```python
# 直接生成
from pdf_report_api import DatePDFReport
gen = DatePDFReport()
pdf_bytes = gen.generate_marry(1990, 1992, start, end)

# API 調用
POST /api/pdf/marry
{
    "man_year": 1990,
    "woman_year": 1992,
    "start_date": "2026-03-01",
    "end_date": "2026-03-31"
}
# 返回 PDF 文件流
```

### 系統總計

| 模組 | 行數 |
|------|-----:|
| main_api.py | 663 |
| pdf_report_api.py | 688 |
| date_base.py | 950 |
| bazi_base.py | 812 |
| marry_date.py | 611 |
| ground_date.py | 709 |
| event_date.py | 467 |
| date_report.py | 573 |
| ziwei_engine_v1.py | 665 |
| meihua_engine.py | 336 |
| chart_matching.py | 487 |
| **總計** | **6961** |

### 日期
2026-02-17

