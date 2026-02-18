# 北斗命數 SaaS - PYLIB 完整索引

> 版本: 2.0.1 (完整版) | 更新: 2026-02-17
> 總文件: 128 ✅ | 總代碼: 45,490 行
> 測試通過率: 100%

---

## 📊 總覽

| 分類 | 文件數 | 代碼行數 |
|------|:------:|--------:|
| 核心引擎 | 25 | 10,180 |
| 命名服務 | 6 | 4,553 |
| 擇日服務 | 7 | 4,227 |
| 其他工具 | 9 | 3,621 |
| 數據服務 | 6 | 2,967 |
| 報告生成 | 5 | 2,736 |
| 部署工具 | 10 | 2,751 |
| 商業閉環 | 10 | 2,598 |
| 前端頁面 | 11 | 2,392 |
| 翻譯對照 | 4 | 2,206 |
| 合婚服務 | 4 | 1,863 |
| API文檔 | 3 | 1,324 |
| 配置監控 | 5 | 753 |
| 認證安全 | 3 | 631 |
| 測試 | 3 | 349 |
| 組件 | 6 | 79 |
| 中間件 | 5 | 75 |
| 任務排程 | 5 | 50 |
| 未分類 | 6 | 2,219 |
| **總計** | **128** | **45,490** |

---

## 🔧 核心引擎 (25 文件 / 10,180 行)

### 八字系統

| 模組 | 行數 | 功能 | 主要函數/類 |
|------|:----:|------|-------------|
| bazi_naming_selector.py | 916 | 八字取名 | `select_name()` |
| bazi_base.py | 812 | 八字核心 | `calculate_bazi()`, `get_pillars()` |
| bazi_advanced.py | 565 | 八字進階 | `analyze_pattern()`, `get_yongshen()` |
| bazi_engine.py | 411 | 八字引擎 | `BaziEngine` |
| bazi_free.py | 120 | 免費試算 | `free_bazi_analyze()` |

### 紫微斗數

| 模組 | 行數 | 功能 | 主要函數/類 |
|------|:----:|------|-------------|
| ziwei_engine_v1.py | 665 | 紫微引擎 | `ZiweiEngine` |
| ziwei_advanced.py | 541 | 紫微進階 | `analyze_palace()` |
| ziwei_liunian.py | 198 | 紫微流年 | `calculate_liunian()` |

### 易經系統

| 模組 | 行數 | 功能 | 主要函數/類 |
|------|:----:|------|-------------|
| yijing_gua_translation.py | 666 | 卦象翻譯 | `GUA_DATA` |
| yijing_yao_translation.py | 573 | 爻辭翻譯 | `YAO_DATA` |
| yijing_qigua_engine_v2.py | 345 | 起卦引擎 | `qigua()` |
| yijing_qigua_engine.py | 233 | 起卦引擎 | `QiguaEngine` |
| yijing_jiegua_v2.py | 228 | 解卦系統 | `jiegua()` |
| yijing_api.py | 83 | 易經API | `yijing_divine()` |
| yijing_config.py | 36 | 易經配置 | `YIJING_CONFIG` |

### 五行系統

| 模組 | 行數 | 功能 | 主要函數/類 |
|------|:----:|------|-------------|
| wuxing_interaction.py | 392 | 五行生剋 | `analyze_interaction()` |
| wuxing_visual.py | 384 | 五行視覺 | `draw_wuxing()` |
| wuxing_analyzer.py | 213 | 五行分析 | `WuxingAnalyzer` |
| wuxing_core.py | 148 | 五行核心 | `WUXING_DATA` |
| wuxing_simple.py | 58 | 五行簡易 | `get_wuxing()` |

### 其他核心

| 模組 | 行數 | 功能 | 主要函數/類 |
|------|:----:|------|-------------|
| qimen_engine_v1.py | 553 | 奇門遁甲 | `QimenEngine` |
| meihua_engine.py | 349 | 梅花易數 | `MeihuaEngine` |
| lunar_calendar_v2.py | 300 | 農曆轉換 | `solar_to_lunar()` |
| liunian_analyzer.py | 244 | 流年分析 | `analyze_liunian()` |
| dayun_calculator.py | 186 | 大運計算 | `calculate_dayun()` |

---

## 📛 命名服務 (6 文件 / 4,553 行)

| 模組 | 行數 | 功能 | 主要函數/類 |
|------|:----:|------|-------------|
| mingshu_naming_marriage_v1.py | 1,314 | 命名婚配 | `NamingMarriage` |
| naming_master.py | 1,117 | 命名大師 | `NamingMaster` |
| naming_selector_v3.py | 822 | 名字選擇 | `select_names()` |
| user_naming_selector.py | 814 | 用戶命名 | `UserNamingSelector` |
| naming_marriage_api.py | 280 | 命名API | `naming_analyze()` |
| mingshu_schema.py | 206 | 命名Schema | `NamingSchema` |

---

## 📅 擇日服務 (7 文件 / 4,227 行)

| 模組 | 行數 | 功能 | 主要函數/類 |
|------|:----:|------|-------------|
| date_base.py | 950 | 擇日核心 | `DateBase` |
| ground_date.py | 709 | 動土擇日 | `ground_date_select()` |
| date_selector_api.py | 624 | 擇日API | `DateSelectorAPI` |
| marry_date.py | 611 | 嫁娶擇日 | `marry_date_select()` |
| date_report.py | 573 | 擇日報告 | `DateReport` |
| event_date.py | 467 | 事件擇日 | `event_date_select()` |
| almanac_filter.py | 293 | 黃曆篩選 | `AlmanacFilter` |

---

## 💑 合婚服務 (4 文件 / 1,863 行)

| 模組 | 行數 | 功能 | 主要函數/類 |
|------|:----:|------|-------------|
| relation_match_report.py | 576 | 合婚報告 | `generate_match_report()` |
| chart_matching.py | 487 | 命盤配對 | `ChartMatching` |
| matching_page.py | 408 | 合婚頁面 | `/matching` |
| relation_analyzer.py | 392 | 關係分析 | `RelationAnalyzer` |

---

## 📄 報告生成 (5 文件 / 2,736 行)

| 模組 | 行數 | 功能 | 主要函數/類 |
|------|:----:|------|-------------|
| pdf_report_api.py | 858 | PDF API | `generate_pdf()` |
| report_generator.py | 831 | 報告引擎 | `ReportGenerator` |
| report_commercial.py | 608 | 商業報告 | `CommercialReport` |
| report_styles.py | 227 | 報告樣式 | `COLORS`, `STYLES` |
| report_charts.py | 212 | 報告圖表 | `create_chart()` |

---

## 🎨 前端頁面 (11 文件 / 2,392 行)

| 模組 | 行數 | 路由 | 功能 |
|------|:----:|------|------|
| user_settings_api.py | 322 | /api/user/settings | 用戶設定 |
| landing_page.py | 320 | / | 落地頁 |
| membership_page.py | 294 | /membership | 會員管理 |
| free_trial.py | 275 | /free | 免費試算 |
| dashboard_v2.py | 252 | /dashboard | 儀表板 |
| pricing_page.py | 240 | /pricing | 定價頁 |
| settings_page.py | 229 | /settings | 設定頁 |
| about_page.py | 198 | /about | 關於頁 |
| faq_page.py | 107 | /help, /faq | FAQ |
| error_pages.py | 88 | /error | 錯誤頁 |

---

## 💳 商業閉環 (10 文件 / 2,598 行)

| 模組 | 行數 | 功能 | 主要類/函數 |
|------|:----:|------|-------------|
| payment_service.py | 465 | 支付服務 | `PaymentService` |
| checkout.py | 424 | 購買頁 | `PRODUCTS`, `/checkout` |
| payment_flow.py | 408 | 支付流程 | `OrderService`, `ECPayService` |
| credits_api.py | 366 | 點數API | `payment_notify()` |
| coupon_service.py | 305 | 優惠券 | `CouponService` |
| invoice_service.py | 303 | 發票服務 | `InvoiceService` |
| membership_service.py | 255 | 會員服務 | `MembershipService` |
| middleware/payment_handler.py | 50 | 支付中間件 | `PaymentHandler` |

---

## 🗄️ 數據服務 (6 文件 / 2,967 行)

| 模組 | 行數 | 功能 | 主要類/函數 |
|------|:----:|------|-------------|
| db_unified.py | 1,137 | 統一數據庫 | `UnifiedDB`, 15 表 |
| admin.py | 453 | 管理後台 | `AdminPanel` |
| saas_api.py | 440 | SaaS API | `SaaSAPI` |
| feedback_system.py | 409 | 反饋系統 | `FeedbackSystem` |
| admin_stats_api.py | 290 | 統計API | `get_stats()` |
| feedback_api.py | 238 | 反饋API | `submit_feedback()` |

---

## 🚀 部署工具 (10 文件 / 2,751 行)

| 模組 | 行數 | 功能 | 主要類/函數 |
|------|:----:|------|-------------|
| deploy/pipeline.py | 547 | 部署流程 | `run_pipeline()`, `Pipeline` |
| deploy/deploy.py | 480 | 部署配置 | `DeployService` |
| deploy/test_all.py | 397 | 測試工具 | `run_all_tests()` |
| task_runner.py | 375 | 任務執行 | `TaskRunner` |
| deploy/launch.py | 363 | 上線檢查 | `LaunchChecklist` |
| deploy/backup.py | 280 | 備份服務 | `BackupService` |
| task_resume.py | 197 | 中斷續作 | `TaskResume`, `resume()` |
| deploy/__init__.py | 45 | 部署初始化 | 導出函數 |
| start.py | 42 | 啟動腳本 | `main()` |
| run_deploy.py | 25 | 部署腳本 | CLI |

---

## ⚙️ 配置監控 (5 文件 / 753 行)

| 模組 | 行數 | 功能 | 主要類/函數 |
|------|:----:|------|-------------|
| logger.py | 303 | 日誌系統 | `Logger`, `setup_logging()` |
| monitoring.py | 216 | 監控追蹤 | `metrics`, `GA4_SCRIPT` |
| config.py | 176 | 統一配置 | `Settings`, `settings` |
| health_check.py | 51 | 健康檢查 | `/api/health` |
| middleware/request_logger.py | 7 | 請求日誌 | `RequestLogger` |

---

## 🔐 認證安全 (3 文件 / 631 行)

| 模組 | 行數 | 功能 | 主要類/函數 |
|------|:----:|------|-------------|
| auth_jwt.py | 344 | JWT認證 | `create_token()`, `verify_token()` |
| security.py | 281 | 安全工具 | `hash_password()`, `verify_password()` |
| middleware/auth_refresh.py | 6 | Token刷新 | `AuthRefresh` |
| middleware/__init__.py | 0 | 初始化 | 導出 |

---

## 📚 翻譯對照 (4 文件 / 2,206 行)

| 模組 | 行數 | 功能 | 主要內容 |
|------|:----:|------|----------|
| field_translation_complete.py | 708 | 欄位翻譯 | `FIELD_MAP` |
| sihua_translation.py | 571 | 四化翻譯 | `SIHUA_DATA` |
| shensha_translation.py | 511 | 神煞翻譯 | `SHENSHA_DATA` |
| fuzhu_star_translation.py | 416 | 輔助星翻譯 | `FUZHU_DATA` |

---

## 📖 API文檔 (3 文件 / 1,324 行)

| 模組 | 行數 | 功能 | 主要內容 |
|------|:----:|------|----------|
| main_api.py | 711 | 主API | 路由整合 |
| api_docs.py | 576 | API文檔 | OpenAPI |
| api_docs_gen.py | 37 | 文檔生成 | `generate_docs()` |

---

## 🛠️ 其他工具 (9 文件 / 3,621 行)

| 模組 | 行數 | 功能 | 主要類/函數 |
|------|:----:|------|-------------|
| five_layer_complete.py | 610 | 五層完整 | `FiveLayer` |
| five_layer_report.py | 581 | 五層報告 | `FiveLayerReport` |
| taoist_connector.py | 514 | 道家連接 | `TaoistConnector` |
| pylib_index.py | 501 | PYLIB索引 | `scan_modules()` |
| geju_analyzer.py | 352 | 格局分析 | `GeJuAnalyzer` |
| wengong_ruler.py | 306 | 文公尺 | `WengongRuler` |
| fortune_timeline.py | 303 | 運勢時間軸 | `FortuneTimeline` |
| doe_analysis.py | 283 | DOE分析 | `DOEAnalysis` |
| divination_query.py | 171 | 占卜查詢 | `DivinationQuery` |

---

## 🔌 中間件 (4 文件 / 35 行)

| 模組 | 行數 | 功能 | 主要函數 |
|------|:----:|------|----------|
| middleware/rate_limiter.py | 13 | API限流 | `rate_limit_middleware()` |
| middleware/error_handler.py | 6 | 錯誤格式 | `error_response()`, `ERROR_CODES` |
| middleware/payment_handler.py | 50 | 支付處理 | `PaymentHandler` |
| middleware/auth_refresh.py | 6 | Token刷新 | `AuthRefresh` |
| middleware/__init__.py | 0 | 初始化 | 導出 |

---

## 🧩 組件 (6 文件 / 79 行)

| 模組 | 行數 | 功能 |
|------|:----:|------|
| components/navbar.py | 23 | 導航欄 |
| components/toast.py | 20 | 提示訊息 |
| components/seo.py | 12 | SEO元標籤 |
| components/footer.py | 12 | 頁腳 |
| components/loading.py | 12 | 載入動畫 |
| components/__init__.py | 0 | 初始化 |

---

## ⏰ 任務排程 (5 文件 / 50 行)

| 模組 | 行數 | 功能 |
|------|:----:|------|
| tasks/order_export.py | 17 | 訂單導出 |
| tasks/payment_timeout.py | 12 | 支付超時 |
| tasks/credits_expiry.py | 10 | 點數過期 |
| tasks/membership_reminder.py | 11 | 會員提醒 |
| tasks/__init__.py | 0 | 初始化 |

---

## 🧪 測試 (3 文件 / 349 行)

| 模組 | 行數 | 功能 |
|------|:----:|------|
| tests/test_api.py | 206 | API測試 |
| tests/test_payment.py | 142 | 支付測試 |
| tests/__init__.py | 1 | 初始化 |

---

## 📁 未分類 (6 文件 / 2,219 行)

| 模組 | 行數 | 功能 | 備註 |
|------|:----:|------|------|
| frontend_app.py | 1,085 | 前端應用 | 舊版 |
| app.py | 477 | 主入口 | FastAPI |
| daxian_calculator.py | 356 | 大限計算 | 核心引擎 |
| email_service.py | 143 | Email服務 | 通知服務 |
| legal_routes.py | 134 | 法務路由 | 前端頁面 |
| app_integration.py | 24 | 應用整合 | 工具 |

---

## 📜 法務文件 (5 文件)

| 文件 | 行數 | 路由 |
|------|:----:|------|
| legal/privacy.md | 74 | /legal/privacy |
| legal/terms.md | 65 | /legal/terms |
| legal/cookie.md | 77 | /legal/cookie |
| legal/refund.md | 35 | /legal/refund |
| legal/disclaimer.md | 45 | /legal/disclaimer |

---

## 🔗 快速查找

| 需求 | 模組 |
|------|------|
| 八字計算 | `bazi_base.py`, `bazi_free.py` |
| 紫微斗數 | `ziwei_engine_v1.py` |
| 易經占卜 | `yijing_qigua_engine_v2.py` |
| 命名取名 | `naming_master.py`, `naming_selector_v3.py` |
| 擇日選日 | `date_base.py`, `date_selector_api.py` |
| 合婚配對 | `chart_matching.py`, `matching_page.py` |
| 支付功能 | `checkout.py` → `payment_flow.py` |
| 報告生成 | `report_generator.py` |
| 統一配置 | `config.py` |
| 部署流程 | `deploy/pipeline.py` |
| 中斷續作 | `task_resume.py` |

---

*PYLIB 完整索引 v2.0.1*
*總計: 128 文件 / 45,490 行*
*XTF8 消-拓-融 | @11星協作 | PYLIB First*
*2026-02-17*
