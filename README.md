# 北斗命數 MVP v3.0

> 古法是根，場論是枝，用戶是花

## 快速開始

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動服務
python main.py

# 訪問
# 前端: http://localhost:8000
# API文檔: http://localhost:8000/docs
```

## 功能

| 功能 | API | 說明 |
|------|-----|------|
| 八字排盤 | `/api/v1/bazi` | 農曆/西曆支援 |
| 紫微斗數 | `/api/v1/ziwei` | 14主星+輔星 |
| 姓名分析 | `/api/v1/name` | 五格+81數理 |
| 梅花易數 | `/api/v1/meihua` | 起卦解卦 |
| 奇門遁甲 | `/api/v1/qimen` | 九星八門 |
| 完整報告 | `/api/v1/full-report` | 綜合分析 |
| 場論翻譯 | `/api/v2/field/*` | 白話化解讀 |

## 系統統計

| 項目 | 數量 |
|------|-----:|
| 康熙筆畫 | 1,481 字 |
| 易經爻辭 | 384 條 |
| 易經卦象 | 64 卦 |
| 十神翻譯 | 10 種 |
| 81數理 | 81 種 |
| API 端點 | 17 個 |

## 部署

### Render 部署

```bash
# 推送到 GitHub 後，Render 自動部署
./deploy.sh
```

或手動：
1. 登入 https://dashboard.render.com
2. New → Web Service
3. 連接 GitHub Repo
4. 自動檢測 `render.yaml` 配置

## 技術棧

- **後端**: FastAPI + Uvicorn
- **數據庫**: SQLite (taoist_v3_enhanced.db, kangxi_20k.db)
- **前端**: 原生 HTML/CSS/JS

---

*北斗七星文創 × 織明 | 2026*
