# 北斗命數 SaaS 部署工具包

> 版本: 1.0.0 | 日期: 2026-02-17
> 方法論: XTF8 消-拓-融 | PYLIB First

---

## 📦 模組結構

```
deploy/
├── __init__.py      # 模組初始化
├── pipeline.py      # 完整流程 (C→B→A→上線)
├── backup.py        # C: 備份
├── test_all.py      # B: 測試  
├── deploy.py        # A: 部署
├── launch.py        # 上線檢查
└── README.md        # 本文檔
```

---

## 🚀 快速使用

### 完整流程

```bash
# 執行完整流程: C備份 → B測試 → A部署 → 上線
python deploy/pipeline.py

# 模擬執行 (不實際操作)
python deploy/pipeline.py --dry-run

# 指定 URL 驗證部署
python deploy/pipeline.py --url https://your-domain.com
```

### 單步執行

```bash
# C: 備份
python deploy/pipeline.py --step C

# B: 測試
python deploy/pipeline.py --step B

# A: 部署
python deploy/pipeline.py --step A

# L: 上線檢查
python deploy/pipeline.py --step L
```

### Python 調用

```python
from deploy import run_pipeline, run_step

# 完整流程
summary = run_pipeline()

# 單步執行
result = run_step('C')  # 備份
result = run_step('B')  # 測試
result = run_step('A')  # 部署
result = run_step('L')  # 上線
```

---

## 📋 模組說明

### C: backup.py (備份)

| 功能 | 說明 |
|------|------|
| `create_full_backup()` | 完整備份 |
| `create_diff_backup()` | 差分備份 |
| `list_backups()` | 列出備份 |
| `notify_telegram()` | 發送通知 |

### B: test_all.py (測試)

| 功能 | 說明 |
|------|------|
| `test_dependencies()` | 依賴檢查 |
| `test_database()` | 數據庫測試 |
| `test_payment_service()` | 支付測試 |
| `test_app_routes()` | 路由測試 |
| `generate_report()` | 生成報告 |

### A: deploy.py (部署)

| 功能 | 說明 |
|------|------|
| `check_prerequisites()` | 前置檢查 |
| `generate_render_config()` | Render 配置 |
| `generate_railway_config()` | Railway 配置 |
| `generate_dockerfile()` | Docker 配置 |
| `generate_deploy_guide()` | 部署指南 |

### L: launch.py (上線)

| 功能 | 說明 |
|------|------|
| `auto_check()` | 自動檢查 |
| `verify_deployment()` | 驗證部署 |
| `get_status()` | 獲取狀態 |
| `RollbackPlan.generate()` | 回滾計劃 |

---

## 📊 流程圖

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   C 備份                                                │
│   ├─ 掃描文件                                           │
│   ├─ 計算 Hash                                          │
│   ├─ 打包壓縮                                           │
│   └─ 發送通知                                           │
│         │                                               │
│         ▼                                               │
│   B 測試                                                │
│   ├─ 依賴檢查                                           │
│   ├─ 模組載入                                           │
│   ├─ 服務測試                                           │
│   └─ 生成報告                                           │
│         │                                               │
│         ▼                                               │
│   A 部署                                                │
│   ├─ 前置檢查                                           │
│   ├─ 生成配置                                           │
│   ├─ Render/Railway/Docker                              │
│   └─ 部署指南                                           │
│         │                                               │
│         ▼                                               │
│   上線                                                  │
│   ├─ P0 必做檢查                                        │
│   ├─ P1 建議檢查                                        │
│   ├─ 驗證部署                                           │
│   └─ 回滾計劃                                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 輸出文件

執行後會生成：

| 文件 | 說明 |
|------|------|
| `backups/*.tar.gz` | 備份壓縮包 |
| `backups/*_manifest.json` | 備份清單 |
| `deploy/test_report.json` | 測試報告 |
| `render.yaml` | Render 配置 |
| `railway.json` | Railway 配置 |
| `Dockerfile` | Docker 配置 |
| `docker-compose.yml` | Docker Compose |
| `.env.template` | 環境變數模板 |
| `deploy/DEPLOY_GUIDE.md` | 部署指南 |
| `deploy/ROLLBACK_PLAN.md` | 回滾計劃 |
| `deploy/launch_state.json` | 上線狀態 |

---

## 🔧 環境變數

```bash
# Telegram 通知 (可選)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

---

*北斗命數 SaaS 部署工具包 v1.0.0*
*XTF8 | PYLIB First | @織明 @星殼*
